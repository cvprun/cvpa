# -*- coding: utf-8 -*-

from contextlib import redirect_stdout
from io import StringIO
from unittest import TestCase, main
from unittest.mock import patch

from cvpa.arguments import version
from cvpa.entrypoint import main as entrypoint_main


class EntrypointTestCase(TestCase):
    def test_version(self):
        buffer = StringIO()
        code = -1
        with redirect_stdout(buffer):
            try:
                entrypoint_main(["--version"])
            except SystemExit as e:
                code = e.code
        self.assertEqual(0, code)
        self.assertEqual(version(), buffer.getvalue().strip())

    @patch("cvpa.entrypoint.run_app", return_value=0)
    def test_no_command(self, mock_run):
        result = entrypoint_main([])
        self.assertEqual(result, 0)
        mock_run.assert_called_once()

    @patch("cvpa.entrypoint.run_app", return_value=0)
    def test_d_flag(self, mock_run):
        result = entrypoint_main(["-D"])
        self.assertEqual(result, 0)
        args = mock_run.call_args[0][1]
        self.assertTrue(args.colored_logging)
        self.assertTrue(args.debug)
        self.assertEqual(args.verbose, 2)

    @patch("cvpa.entrypoint.run_app", return_value=0)
    def test_debug_flag(self, mock_run):
        result = entrypoint_main(["--debug"])
        self.assertEqual(result, 0)
        args = mock_run.call_args[0][1]
        self.assertEqual(args.logging_severity, "debug")

    @patch("cvpa.entrypoint.run_app", return_value=0)
    def test_colored_logging(self, mock_run):
        result = entrypoint_main(["--colored-logging"])
        self.assertEqual(result, 0)

    @patch("cvpa.entrypoint.run_app", return_value=0)
    def test_simple_logging(self, mock_run):
        result = entrypoint_main(["--simple-logging"])
        self.assertEqual(result, 0)


if __name__ == "__main__":
    main()
