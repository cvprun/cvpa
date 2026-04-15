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
            slug="slug1",
            token="token1",
        )
        agent_main(args)
        mock_app_cls.assert_called_once()
        mock_app_cls.return_value.start.assert_called_once()


if __name__ == "__main__":
    main()
