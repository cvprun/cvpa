# -*- coding: utf-8 -*-

from argparse import Namespace
from unittest import TestCase, main
from unittest.mock import MagicMock, patch

from cvpa.apps import build_app, run_app
from cvpa.apps.idle import IdleApp
from cvpa.arguments import CMD_AGENT


def _standalone_args(token: str = "") -> Namespace:
    return Namespace(
        cmd=CMD_AGENT,
        token=token,
        uri="ws://test",
        use_uvloop=False,
        debug=False,
        slow_callback_duration=0.05,
    )


class BuildAppTestCase(TestCase):
    def test_agent_returns_idle_app(self):
        app = build_app(CMD_AGENT, _standalone_args())
        self.assertIsInstance(app, IdleApp)

    def test_unknown_cmd_raises(self):
        with self.assertRaises(ValueError):
            build_app("nonexistent_cmd", _standalone_args())


class RunAppTestCase(TestCase):
    def test_unknown_command_returns_one(self):
        result = run_app("nonexistent_cmd", _standalone_args())
        self.assertEqual(result, 1)

    @patch("cvpa.apps.StandaloneRuntime")
    def test_standalone_path(self, mock_runtime_cls):
        mock_runtime = MagicMock()
        mock_runtime.execute.return_value = 0
        mock_runtime_cls.return_value = mock_runtime

        result = run_app(CMD_AGENT, _standalone_args(token=""))
        self.assertEqual(result, 0)
        mock_runtime.execute.assert_called_once()
        self.assertIsInstance(mock_runtime.execute.call_args.args[0], IdleApp)

    @patch("cvpa.apps.ConnectedRuntime")
    def test_connected_path_with_token(self, mock_runtime_cls):
        mock_runtime = MagicMock()
        mock_runtime.execute.return_value = 0
        mock_runtime_cls.return_value = mock_runtime

        args = _standalone_args(token="cvp_abc123_myslug")
        result = run_app(CMD_AGENT, args)
        self.assertEqual(result, 0)
        mock_runtime_cls.assert_called_once()
        kwargs = mock_runtime_cls.call_args.kwargs
        self.assertEqual(kwargs["slug"], "myslug")
        self.assertEqual(kwargs["token"], "cvp_abc123")
        mock_runtime.execute.assert_called_once()


if __name__ == "__main__":
    main()
