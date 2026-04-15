# -*- coding: utf-8 -*-

from argparse import Namespace
from asyncio.exceptions import CancelledError
from unittest import TestCase, main
from unittest.mock import MagicMock, patch

from cvpa.apps import run_app


class RunAppTestCase(TestCase):
    def test_unknown_command(self):
        result = run_app("nonexistent_cmd", Namespace())
        self.assertEqual(result, 1)

    @patch("cvpa.apps.cmd_apps")
    def test_success(self, mock_apps):
        mock_fn = MagicMock()
        mock_apps.return_value = {"test": mock_fn}
        result = run_app("test", Namespace())
        self.assertEqual(result, 0)
        mock_fn.assert_called_once()

    @patch("cvpa.apps.cmd_apps")
    def test_cancelled_error(self, mock_apps):
        mock_fn = MagicMock(side_effect=CancelledError)
        mock_apps.return_value = {"test": mock_fn}
        result = run_app("test", Namespace())
        self.assertEqual(result, 0)

    @patch("cvpa.apps.cmd_apps")
    def test_keyboard_interrupt(self, mock_apps):
        mock_fn = MagicMock(side_effect=KeyboardInterrupt)
        mock_apps.return_value = {"test": mock_fn}
        result = run_app("test", Namespace())
        self.assertEqual(result, 0)

    @patch("cvpa.apps.cmd_apps")
    def test_interrupted_error(self, mock_apps):
        mock_fn = MagicMock(side_effect=InterruptedError)
        mock_apps.return_value = {"test": mock_fn}
        result = run_app("test", Namespace())
        self.assertEqual(result, 0)

    @patch("cvpa.apps.cmd_apps")
    def test_system_exit_zero(self, mock_apps):
        mock_fn = MagicMock(side_effect=SystemExit(0))
        mock_apps.return_value = {"test": mock_fn}
        result = run_app("test", Namespace())
        self.assertEqual(result, 0)

    @patch("cvpa.apps.cmd_apps")
    def test_system_exit_nonzero(self, mock_apps):
        mock_fn = MagicMock(side_effect=SystemExit(1))
        mock_apps.return_value = {"test": mock_fn}
        result = run_app("test", Namespace())
        self.assertEqual(result, 1)

    @patch("cvpa.apps.cmd_apps")
    def test_generic_exception(self, mock_apps):
        mock_fn = MagicMock(side_effect=RuntimeError("boom"))
        mock_apps.return_value = {"test": mock_fn}
        result = run_app("test", Namespace())
        self.assertEqual(result, 1)


if __name__ == "__main__":
    main()
