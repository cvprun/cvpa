# -*- coding: utf-8 -*-

from unittest import TestCase, main
from unittest.mock import MagicMock, patch


async def _noop():
    pass


class AioRunTestCase(TestCase):
    @patch("cvpa.aio.run.asyncio_run")
    def test_without_uvloop(self, mock_run):
        from cvpa.aio.run import aio_run

        coro = _noop()
        aio_run(coro, use_uvloop=False)
        mock_run.assert_called_once_with(coro)

    @patch("cvpa.aio.run.uv_run")
    def test_with_uvloop(self, mock_uv_run):
        from cvpa.aio.run import aio_run

        coro = _noop()
        aio_run(coro, use_uvloop=True)
        mock_uv_run.assert_called_once_with(coro)


class UvRunTestCase(TestCase):
    def test_python_3_11_plus(self):
        mock_runner = MagicMock()
        mock_runner.__enter__ = MagicMock(return_value=mock_runner)
        mock_runner.__exit__ = MagicMock(return_value=False)

        with patch("cvpa.aio.run.version_info", (3, 14)):
            with patch("asyncio.Runner", return_value=mock_runner, create=True):
                with patch("uvloop.new_event_loop"):
                    from cvpa.aio.run import uv_run

                    coro = _noop()
                    uv_run(coro)
                    mock_runner.run.assert_called_once_with(coro)

    def test_python_below_3_11(self):
        with patch("cvpa.aio.run.version_info", (3, 10)):
            with patch("uvloop.install") as mock_install:
                with patch("cvpa.aio.run.asyncio_run") as mock_run:
                    from cvpa.aio.run import uv_run

                    coro = _noop()
                    uv_run(coro)
                    mock_install.assert_called_once()
                    mock_run.assert_called_once_with(coro)


if __name__ == "__main__":
    main()
