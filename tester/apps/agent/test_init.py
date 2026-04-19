# -*- coding: utf-8 -*-

from argparse import Namespace
from unittest import TestCase, main
from unittest.mock import patch


class AgentMainTestCase(TestCase):
    @patch("cvpa.apps.agent.app.AgentApplication")
    def test_agent_main(self, mock_app_cls):
        from cvpa.apps.agent import agent_main

        args = Namespace(
            logging_step=1000,
            use_uvloop=False,
            slow_callback_duration=0.05,
            debug=False,
            verbose=0,
            uri="ws://test",
            token="cvp_abc123_myslug",
        )
        agent_main(args)
        mock_app_cls.assert_called_once()
        kwargs = mock_app_cls.call_args.kwargs
        self.assertEqual(kwargs["slug"], "myslug")
        self.assertEqual(kwargs["token"], "cvp_abc123")
        mock_app_cls.return_value.start.assert_called_once()

    def test_agent_main_invalid_token(self):
        from cvpa.apps.agent import agent_main

        args = Namespace(
            logging_step=1000,
            use_uvloop=False,
            slow_callback_duration=0.05,
            debug=False,
            verbose=0,
            uri="ws://test",
            token="invalid_token",
        )
        with self.assertRaises(ValueError):
            agent_main(args)


if __name__ == "__main__":
    main()
