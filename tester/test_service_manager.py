# -*- coding: utf-8 -*-

from unittest import TestCase, main
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from cvpa.service.manager import ServiceManager


def _make_manager():
    return ServiceManager(logger=MagicMock())


class ServiceManagerSyncTestCase(TestCase):
    @patch("cvpa.service.manager.ProcessService")
    def test_add(self, mock_ps):
        mgr = _make_manager()
        mgr.add("svc1", ["cmd"], on_message=AsyncMock())
        self.assertIn("svc1", mgr._services)

    @patch("cvpa.service.manager.ProcessService")
    def test_add_duplicate_raises(self, mock_ps):
        mgr = _make_manager()
        mgr.add("svc1", ["cmd"], on_message=AsyncMock())
        with self.assertRaises(ValueError):
            mgr.add("svc1", ["cmd"], on_message=AsyncMock())

    @patch("cvpa.service.manager.ProcessService")
    def test_list_services(self, mock_ps):
        mgr = _make_manager()
        mock_svc = MagicMock()
        mock_svc.is_alive = False
        mock_ps.return_value = mock_svc
        mgr.add("svc1", ["cmd"], on_message=AsyncMock())
        result = mgr.list_services()
        self.assertEqual(result, {"svc1": False})


@patch("cvpa.service.manager.ProcessService")
async def test_start(mock_ps):
    mgr = _make_manager()
    mock_svc = AsyncMock()
    mock_ps.return_value = mock_svc
    mgr.add("svc1", ["cmd"], on_message=AsyncMock())
    await mgr.start("svc1")
    assert "svc1" in mgr._tasks


@patch("cvpa.service.manager.ProcessService")
async def test_start_all(mock_ps):
    mgr = _make_manager()
    mock_ps.return_value = AsyncMock()
    mgr.add("svc1", ["cmd"], on_message=AsyncMock())
    mgr.add("svc2", ["cmd2"], on_message=AsyncMock())
    await mgr.start_all()
    assert len(mgr._tasks) == 2


@patch("cvpa.service.manager.ProcessService")
async def test_stop(mock_ps):
    mgr = _make_manager()
    mock_svc = AsyncMock()
    mock_ps.return_value = mock_svc
    mgr.add("svc1", ["cmd"], on_message=AsyncMock())
    await mgr.start("svc1")
    await mgr.stop("svc1")
    mock_svc.stop.assert_awaited_once()


@patch("cvpa.service.manager.ProcessService")
async def test_stop_no_task(mock_ps):
    mgr = _make_manager()
    mock_svc = AsyncMock()
    mock_ps.return_value = mock_svc
    mgr.add("svc1", ["cmd"], on_message=AsyncMock())
    await mgr.stop("svc1")
    mock_svc.stop.assert_awaited_once()


@patch("cvpa.service.manager.ProcessService")
async def test_stop_all(mock_ps):
    mgr = _make_manager()
    mock_ps.return_value = AsyncMock()
    mgr.add("svc1", ["cmd"], on_message=AsyncMock())
    mgr.add("svc2", ["cmd2"], on_message=AsyncMock())
    await mgr.start_all()
    await mgr.stop_all()


@patch("cvpa.service.manager.ProcessService")
async def test_send(mock_ps):
    mgr = _make_manager()
    mock_svc = AsyncMock()
    mock_ps.return_value = mock_svc
    mgr.add("svc1", ["cmd"], on_message=AsyncMock())
    await mgr.send("svc1", {"key": "val"})
    mock_svc.send.assert_awaited_once_with({"key": "val"})


if __name__ == "__main__":
    main()
