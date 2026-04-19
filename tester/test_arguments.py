# -*- coding: utf-8 -*-

import tempfile
from unittest import TestCase, main
from unittest.mock import patch

from cvpa.arguments import (
    _inject_default_subcommand,
    _load_dotenv,
    _remove_dotenv_attrs,
    cvp_home,
    default_argument_parser,
    get_default_arguments,
    version,
)


class VersionTestCase(TestCase):
    def test_returns_string(self):
        v = version()
        self.assertIsInstance(v, str)
        self.assertGreater(len(v), 0)


class CvpHomeTestCase(TestCase):
    def test_ends_with_cvpa(self):
        home = cvp_home()
        self.assertTrue(home.endswith(".cvpa"))


class DefaultArgumentParserTestCase(TestCase):
    def test_returns_parser(self):
        parser = default_argument_parser()
        self.assertIsNotNone(parser)


class GetDefaultArgumentsTestCase(TestCase):
    def test_agent_command(self):
        args = get_default_arguments(["agent", "cvp_slug1_tok1", "--uri", "ws://test"])
        self.assertEqual(args.cmd, "agent")
        self.assertEqual(args.uri, "ws://test")
        self.assertEqual(args.token, "cvp_slug1_tok1")

    def test_agent_command_default_uri(self):
        args = get_default_arguments(["agent", "cvp_slug1_tok1"])
        self.assertEqual(args.cmd, "agent")
        self.assertEqual(args.uri, "https://app.cvp.run/")
        self.assertEqual(args.token, "cvp_slug1_tok1")

    def test_agent_command_auto_inject(self):
        args = get_default_arguments(["cvp_slug1_tok1"])
        self.assertEqual(args.cmd, "agent")
        self.assertEqual(args.token, "cvp_slug1_tok1")

    def test_debug_flag(self):
        args = get_default_arguments(["--debug", "agent"])
        self.assertTrue(args.debug)

    def test_d_flag(self):
        args = get_default_arguments(["-D", "agent"])
        self.assertTrue(args.D)

    def test_no_command(self):
        args = get_default_arguments([])
        self.assertIsNone(args.cmd)


class InjectDefaultSubcommandTestCase(TestCase):
    def test_already_has_agent(self):
        result = _inject_default_subcommand(["agent", "cvp_x_y"])
        self.assertEqual(result, ["agent", "cvp_x_y"])

    def test_inject_before_token(self):
        result = _inject_default_subcommand(["cvp_x_y"])
        self.assertEqual(result, ["agent", "cvp_x_y"])

    def test_inject_after_flags(self):
        result = _inject_default_subcommand(["--debug", "cvp_x_y"])
        self.assertEqual(result, ["--debug", "agent", "cvp_x_y"])

    def test_no_token_no_inject(self):
        result = _inject_default_subcommand(["--debug"])
        self.assertEqual(result, ["--debug"])

    def test_none_reads_sys_argv(self):
        import sys

        original = sys.argv
        sys.argv = ["cvpa", "cvp_x_y"]
        try:
            result = _inject_default_subcommand(None)
            self.assertEqual(result, ["agent", "cvp_x_y"])
        finally:
            sys.argv = original


class LoadDotenvTestCase(TestCase):
    def test_no_dotenv(self):
        _load_dotenv(["--no-dotenv"])

    def test_nonexistent_file(self):
        _load_dotenv(["--dotenv-path", "/nonexistent/path/.env"])

    def test_unreadable_file(self):
        with tempfile.NamedTemporaryFile(suffix=".env", delete=False) as f:
            f.write(b"KEY=VALUE")
            f.flush()
            import os

            os.chmod(f.name, 0o000)
            try:
                _load_dotenv(["--dotenv-path", f.name])
            finally:
                os.chmod(f.name, 0o644)

    def test_valid_dotenv(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".env", delete=False) as f:
            f.write("_CVPA_TEST_DOTENV_=hello\n")
            f.flush()
            _load_dotenv(["--dotenv-path", f.name])

    def test_missing_dotenv_module(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".env", delete=False) as f:
            f.write("KEY=VALUE\n")
            f.flush()
            with patch("cvpa.arguments.isfile", return_value=True):
                with patch("cvpa.arguments.access", return_value=True):
                    with patch.dict("sys.modules", {"dotenv": None}):
                        _load_dotenv(["--dotenv-path", f.name])


class RemoveDotenvAttrsTestCase(TestCase):
    def test_removes_attrs(self):
        from argparse import Namespace

        ns = Namespace(no_dotenv=False, dotenv_path="/tmp/.env", other="val")
        result = _remove_dotenv_attrs(ns)
        self.assertFalse(hasattr(result, "no_dotenv"))
        self.assertFalse(hasattr(result, "dotenv_path"))
        self.assertEqual(result.other, "val")


if __name__ == "__main__":
    main()
