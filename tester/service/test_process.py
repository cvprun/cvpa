# -*- coding: utf-8 -*-

import asyncio
from unittest import TestCase, main
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from cvpa.service.process import ProcessService


def _make_service(**kwargs):
    return ProcessService(
        kwargs.get("name", "test"),
        kwargs.get("cmd", ["echo"]),
        on_message=kwargs.get("on_message", AsyncMock()),
        auto_restart=kwargs.get("auto_restart", False),
        logger=kwargs.get("logger", MagicMock()),
    )


class ProcessServiceSyncTestCase(TestCase):
    def test_socket_path(self):
        svc = _make_service()
        self.assertIn("test", svc.socket_path)
        self.assertTrue(svc.socket_path.startswith("/tmp/cvpa-"))

    def test_is_alive_no_process(self):
        svc = _make_service()
        self.assertFalse(svc.is_alive)

    def test_is_alive_running(self):
        svc = _make_service()
        svc._process = MagicMock()
        svc._process.returncode = None
        self.assertTrue(svc.is_alive)

    def test_is_alive_exited(self):
        svc = _make_service()
        svc._process = MagicMock()
        svc._process.returncode = 0
        self.assertFalse(svc.is_alive)


@patch("cvpa.service.process.sleep", new_callable=AsyncMock)
async def test_wait_for_socket_found(mock_sleep):
    svc = _make_service()
    with patch("cvpa.service.process.Path") as mock_path:
        mock_path.return_value.exists.return_value = True
        result = await svc._wait_for_socket()
        assert result is True


@patch("cvpa.service.process.sleep", new_callable=AsyncMock)
@patch("cvpa.service.process.SOCKET_WAIT_TIMEOUT", 0.05)
@patch("cvpa.service.process.SOCKET_WAIT_INTERVAL", 0.01)
async def test_wait_for_socket_timeout(mock_sleep):
    svc = _make_service()
    with patch("cvpa.service.process.Path") as mock_path:
        mock_path.return_value.exists.return_value = False
        result = await svc._wait_for_socket()
        assert result is False


@patch("cvpa.service.process.sleep", new_callable=AsyncMock)
async def test_wait_for_socket_stopped(mock_sleep):
    svc = _make_service()
    svc._stop_event.set()
    result = await svc._wait_for_socket()
    assert result is False


@patch("cvpa.service.process.create_subprocess_exec")
async def test_spawn(mock_exec):
    mock_process = MagicMock()
    mock_exec.return_value = mock_process
    svc = _make_service()
    await svc._spawn()
    assert svc._process is mock_process


@patch("cvpa.service.process.grpc.aio.insecure_channel")
@patch("cvpa.service.process.ManagedServiceStub")
async def test_connect_success(mock_stub_cls, mock_channel):
    svc = _make_service()
    with patch.object(svc, "_wait_for_socket", return_value=True):
        await svc._connect()
        assert svc._channel is not None
        assert svc._stub is not None


async def test_connect_socket_not_ready():
    svc = _make_service()
    with patch.object(svc, "_wait_for_socket", return_value=False):
        with pytest.raises(RuntimeError):
            await svc._connect()


async def test_cleanup_channel():
    svc = _make_service()
    svc._channel = AsyncMock()
    svc._stub = MagicMock()
    await svc._cleanup_channel()
    assert svc._channel is None
    assert svc._stub is None


async def test_cleanup_channel_none():
    svc = _make_service()
    await svc._cleanup_channel()


async def test_cleanup_socket():
    svc = _make_service()
    with patch("cvpa.service.process.unlink") as mock_unlink:
        await svc._cleanup_socket()
        mock_unlink.assert_called_once_with(svc.socket_path)


async def test_cleanup_socket_not_found():
    svc = _make_service()
    with patch("cvpa.service.process.unlink", side_effect=FileNotFoundError):
        await svc._cleanup_socket()


async def test_send_no_stub():
    svc = _make_service()
    with pytest.raises(RuntimeError):
        await svc.send({"key": "val"})


async def test_send_with_stub():
    svc = _make_service()
    mock_stub = MagicMock()

    class FakeAsyncIter:
        def __aiter__(self):
            return self

        async def __anext__(self):
            raise StopAsyncIteration

    mock_stub.Channel.return_value = FakeAsyncIter()
    svc._stub = mock_stub
    await svc.send({})


async def test_stop_with_stub():
    svc = _make_service()
    svc._stub = AsyncMock()
    svc._channel = AsyncMock()
    await svc.stop()
    assert svc._stop_event.is_set()


async def test_stop_with_running_process():
    svc = _make_service()
    mock_process = AsyncMock()
    mock_process.returncode = None
    mock_process.wait = AsyncMock()
    svc._process = mock_process
    svc._channel = AsyncMock()
    await svc.stop()
    assert svc._stop_event.is_set()


async def test_stop_with_process_timeout():
    svc = _make_service()
    mock_process = MagicMock()
    mock_process.returncode = None
    mock_process.kill = MagicMock()
    mock_process.wait = AsyncMock()
    svc._process = mock_process
    svc._channel = AsyncMock()

    with patch(
        "cvpa.service.process.asyncio.wait_for",
        side_effect=asyncio.TimeoutError,
    ):
        await svc.stop()
        mock_process.kill.assert_called_once()


async def test_stop_stub_shutdown_exception():
    svc = _make_service()
    mock_stub = AsyncMock()
    mock_stub.Shutdown.side_effect = RuntimeError("fail")
    svc._stub = mock_stub
    svc._channel = AsyncMock()
    await svc.stop()


async def test_drain_stderr():
    svc = _make_service()
    mock_process = MagicMock()

    async def fake_iter():
        yield b"line1\n"
        yield b"line2\n"

    mock_process.stderr = fake_iter()
    svc._process = mock_process
    await svc._drain_stderr()


async def test_drain_stderr_empty_line():
    svc = _make_service()
    mock_process = MagicMock()

    async def fake_iter():
        yield b"\n"

    mock_process.stderr = fake_iter()
    svc._process = mock_process
    await svc._drain_stderr()


@patch("cvpa.service.process.sleep", new_callable=AsyncMock)
async def test_start_exception_then_sleep_stop(mock_sleep):
    """Exception in start loop, then stop via sleep side_effect."""
    svc = _make_service(auto_restart=True)

    with patch.object(svc, "_spawn", side_effect=RuntimeError("fail")):
        with patch.object(svc, "_cleanup_channel", new_callable=AsyncMock):

            async def set_stop(*args):
                svc._stop_event.set()

            mock_sleep.side_effect = set_stop
            await svc.start()


async def test_start_exception_with_stop_event_set():
    """Exception while stop_event already set -> break at line 117."""
    svc = _make_service(auto_restart=True)

    def spawn_and_stop():
        svc._stop_event.set()
        raise RuntimeError("fail")

    with patch.object(svc, "_spawn", side_effect=spawn_and_stop):
        with patch.object(svc, "_cleanup_channel", new_callable=AsyncMock):
            await svc.start()


async def test_run_channel():
    svc = _make_service()
    mock_stub = MagicMock()

    class FakeCall:
        def __aiter__(self):
            return self

        def __init__(self):
            self._items = iter([MagicMock()])

        async def __anext__(self):
            try:
                return next(self._items)
            except StopIteration:
                raise StopAsyncIteration

    mock_stub.Channel.return_value = FakeCall()
    svc._stub = mock_stub
    await svc._run_channel()


@patch("cvpa.service.process.sleep", new_callable=AsyncMock)
@patch("cvpa.service.process.create_subprocess_exec")
@patch("cvpa.service.process.grpc.aio.insecure_channel")
@patch("cvpa.service.process.ManagedServiceStub")
async def test_start_full_loop(mock_stub_cls, mock_channel_fn, mock_exec, mock_sleep):
    """Cover the full start loop including pending task cancellation (line 113)."""
    import asyncio as aio

    svc = _make_service(auto_restart=False)

    mock_process = MagicMock()
    mock_process.returncode = None
    # process.wait() resolves quickly
    mock_process.wait = AsyncMock(return_value=0)

    # stderr hangs (will be in pending)
    stderr_event = aio.Event()

    async def slow_stderr():
        await stderr_event.wait()
        yield b""

    mock_process.stderr = slow_stderr()
    mock_exec.return_value = mock_process
    mock_channel_fn.return_value = AsyncMock()

    # channel also hangs (will be in pending)
    class HangingCall:
        def __aiter__(self):
            return self

        async def __anext__(self):
            await aio.Event().wait()  # hang forever

    mock_stub_cls.return_value.Channel.return_value = HangingCall()

    with patch.object(svc, "_wait_for_socket", return_value=True):
        # process.wait() finishes first, stderr + channel remain pending -> cancel
        mock_process.returncode = 0
        await svc.start()


@patch("cvpa.service.process.sleep", new_callable=AsyncMock)
@patch("cvpa.service.process.create_subprocess_exec")
@patch("cvpa.service.process.grpc.aio.insecure_channel")
@patch("cvpa.service.process.ManagedServiceStub")
async def test_start_auto_restart_then_stop(
    mock_stub_cls, mock_channel_fn, mock_exec, mock_sleep
):
    """Cover auto_restart=True path that restarts then stops."""
    svc = _make_service(auto_restart=True)

    mock_process = MagicMock()
    mock_process.returncode = 1
    mock_process.wait = AsyncMock(return_value=1)

    async def fake_stderr():
        return
        yield  # noqa

    mock_process.stderr = fake_stderr()
    mock_exec.return_value = mock_process
    mock_channel_fn.return_value = AsyncMock()

    class FakeCall:
        def __aiter__(self):
            return self

        async def __anext__(self):
            raise StopAsyncIteration

    mock_stub_cls.return_value.Channel.return_value = FakeCall()

    with patch.object(svc, "_wait_for_socket", return_value=True):

        async def stop_on_sleep(*args):
            svc._stop_event.set()

        mock_sleep.side_effect = stop_on_sleep
        await svc.start()


async def test_send_with_stub_iter():
    """Cover line 150: async for _ in call: pass."""
    svc = _make_service()
    mock_stub = MagicMock()

    class FakeCall:
        def __aiter__(self):
            return self

        def __init__(self):
            self._items = iter([MagicMock()])

        async def __anext__(self):
            try:
                return next(self._items)
            except StopIteration:
                raise StopAsyncIteration

    mock_stub.Channel.return_value = FakeCall()
    svc._stub = mock_stub
    await svc.send({})


if __name__ == "__main__":
    main()
