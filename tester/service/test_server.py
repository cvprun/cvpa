# -*- coding: utf-8 -*-

from asyncio import Event
from logging import getLogger
from unittest import TestCase, main
from unittest.mock import AsyncMock, MagicMock, patch

from cvpa.protos.service_pb2 import Empty, Envelope, Pat, Pit
from cvpa.service.server import ServiceServer, _Servicer


class ServicerSyncTestCase(TestCase):
    def _make_servicer(self):
        return _Servicer(
            on_envelope=AsyncMock(),
            stop_event=Event(),
            logger=getLogger("test"),
        )

    def test_enqueue(self):
        s = self._make_servicer()
        env = Envelope()
        s.enqueue(env)
        self.assertEqual(len(s._outbox), 1)
        self.assertTrue(s._outbox_event.is_set())


class ServiceServerSyncTestCase(TestCase):
    def test_init(self):
        srv = ServiceServer("/tmp/test.sock", on_envelope=AsyncMock())
        self.assertIsNotNone(srv._servicer)


async def test_heartbeat():
    s = _Servicer(
        on_envelope=AsyncMock(),
        stop_event=Event(),
        logger=getLogger("test"),
    )
    result = await s.Heartbeat(Pit(), MagicMock())
    assert isinstance(result, Pat)
    assert result.ok


async def test_shutdown():
    s = _Servicer(
        on_envelope=AsyncMock(),
        stop_event=Event(),
        logger=getLogger("test"),
    )
    result = await s.Shutdown(Empty(), MagicMock())
    assert isinstance(result, Empty)
    assert s._stop_event.is_set()


async def test_send():
    srv = ServiceServer("/tmp/test.sock", on_envelope=AsyncMock())
    env = Envelope()
    await srv.send(env)
    assert len(srv._servicer._outbox) == 1


@patch("cvpa.service.server.grpc.aio.server")
@patch("cvpa.service.server.add_ManagedServiceServicer_to_server")
async def test_serve(mock_add, mock_server_fn):
    mock_server = AsyncMock()
    mock_server_fn.return_value = mock_server

    srv = ServiceServer(
        "/tmp/test.sock", on_envelope=AsyncMock(), logger=getLogger("test")
    )
    srv._stop_event.set()
    await srv.serve()
    mock_server.start.assert_awaited_once()
    mock_server.stop.assert_awaited_once()


async def test_channel():
    """Test _Servicer.Channel async generator."""
    import asyncio

    on_envelope = AsyncMock()
    stop_event = Event()
    s = _Servicer(
        on_envelope=on_envelope, stop_event=stop_event, logger=getLogger("test")
    )

    # Create a request iterator that yields one envelope then stops
    req_envelope = Envelope()

    async def fake_request_iter():
        yield req_envelope

    # Enqueue an outgoing envelope
    out_envelope = Envelope()
    s.enqueue(out_envelope)

    # Schedule stop after a short delay
    async def stop_later():
        await asyncio.sleep(0.01)
        stop_event.set()
        s._outbox_event.set()

    stop_task = asyncio.create_task(stop_later())

    results = []
    async for env in s.Channel(fake_request_iter(), MagicMock()):
        results.append(env)

    await stop_task
    assert len(results) >= 1
    on_envelope.assert_awaited_once_with(req_envelope)


if __name__ == "__main__":
    main()
