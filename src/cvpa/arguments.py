# -*- coding: utf-8 -*-

from argparse import ArgumentParser, Namespace, RawDescriptionHelpFormatter
from functools import lru_cache
from os import R_OK, access, getcwd
from os.path import expanduser, isfile, join
from typing import Final, List, Optional, Sequence

from cvpa.logging.logging import SEVERITIES, SEVERITY_NAME_INFO
from cvpa.system.environ import get_typed_environ_value as get_eval
from cvpa.system.environ_keys import (
    CVPA_AGENT_TOKEN,
    CVPA_AGENT_URL,
    CVPA_COLORED_LOGGING,
    CVPA_DEBUG,
    CVPA_DOTENV_PATH,
    CVPA_HOME,
    CVPA_LOGGING_SEVERITY,
    CVPA_LOGGING_STEP,
    CVPA_NO_DOTENV,
    CVPA_SIMPLE_LOGGING,
    CVPA_SLOW_CALLBACK_DURATION,
    CVPA_USE_UVLOOP,
    CVPA_VERBOSE,
)
from cvpa.variables import (
    AGENT_TOKEN_PREFIX,
    CVPA_HOME_DIRNAME,
    DEFAULT_CVPA_URL,
    DOTENV_LOCAL_FILENAME,
    LOGGING_STEP,
    SLOW_CALLBACK_DURATION,
)

PROG: Final[str] = "cvpa"
DESCRIPTION: Final[str] = "Computer Vision Player Agent"
EPILOG: Final[str] = ""

CMD_AGENT: Final[str] = "agent"
CMD_AGENT_HELP: Final[str] = "Background agent"
CMD_AGENT_EPILOG = f"""
Simply usage:
  {PROG} {CMD_AGENT}
"""

CMDS: Final[Sequence[str]] = (CMD_AGENT,)

DEFAULT_SEVERITY: Final[str] = SEVERITY_NAME_INFO


@lru_cache
def version() -> str:
    # [IMPORTANT] Avoid 'circular import' issues
    from cvpa import __version__

    return __version__


@lru_cache
def cvp_home() -> str:
    return join(expanduser("~"), CVPA_HOME_DIRNAME)


def add_dotenv_arguments(parser: ArgumentParser) -> None:
    parser.add_argument(
        "--no-dotenv",
        action="store_true",
        default=get_eval(CVPA_NO_DOTENV, False),
        help="Do not use dot-env file",
    )
    parser.add_argument(
        "--dotenv-path",
        default=get_eval(CVPA_DOTENV_PATH, join(getcwd(), DOTENV_LOCAL_FILENAME)),
        metavar="file",
        help=f"Specifies the dot-env file (default: '{DOTENV_LOCAL_FILENAME}')",
    )


def add_agent_parser(subparsers) -> None:
    # noinspection SpellCheckingInspection
    parser = subparsers.add_parser(
        name=CMD_AGENT,
        help=CMD_AGENT_HELP,
        formatter_class=RawDescriptionHelpFormatter,
        epilog=CMD_AGENT_EPILOG,
    )
    assert isinstance(parser, ArgumentParser)

    parser.add_argument(
        "token",
        nargs="?",
        default=get_eval(CVPA_AGENT_TOKEN, ""),
        help=(
            f"Combined agent token in the form '{AGENT_TOKEN_PREFIX}{{slug}}_{{token}}'"
            " (or set CVPA_AGENT_TOKEN)"
        ),
    )
    parser.add_argument(
        "--uri",
        default=get_eval(CVPA_AGENT_URL, DEFAULT_CVPA_URL),
        help=(
            "Base URL prefix of the CVPA service "
            f"(default: '{DEFAULT_CVPA_URL}', or set CVPA_AGENT_URL)"
        ),
    )


def default_argument_parser() -> ArgumentParser:
    parser = ArgumentParser(
        prog=PROG,
        description=DESCRIPTION,
        epilog=EPILOG,
        formatter_class=RawDescriptionHelpFormatter,
    )

    add_dotenv_arguments(parser)

    home_path = cvp_home()
    parser.add_argument(
        "--home",
        metavar="dir",
        default=get_eval(CVPA_HOME, home_path),
        help=f"{PROG}'s home directory (default: '{home_path}')",
    )

    logging_group = parser.add_mutually_exclusive_group()
    logging_group.add_argument(
        "--colored-logging",
        "-c",
        action="store_true",
        default=get_eval(CVPA_COLORED_LOGGING, False),
        help="Use colored logging",
    )
    logging_group.add_argument(
        "--simple-logging",
        "-s",
        action="store_true",
        default=get_eval(CVPA_SIMPLE_LOGGING, False),
        help="Use simple logging",
    )

    parser.add_argument(
        "--logging-step",
        type=int,
        default=get_eval(CVPA_LOGGING_STEP, LOGGING_STEP),
        help="An iterative step that emits statistics results to a logger",
    )
    parser.add_argument(
        "--logging-severity",
        choices=SEVERITIES,
        default=get_eval(CVPA_LOGGING_SEVERITY, DEFAULT_SEVERITY),
        help=f"Logging severity (default: '{DEFAULT_SEVERITY}')",
    )

    parser.add_argument(
        "--use-uvloop",
        action="store_true",
        default=get_eval(CVPA_USE_UVLOOP, False),
        help="Replace the event loop with uvloop",
    )
    parser.add_argument(
        "--slow-callback-duration",
        type=float,
        default=get_eval(CVPA_SLOW_CALLBACK_DURATION, SLOW_CALLBACK_DURATION),
        help=(
            "Slow callback duration threshold in seconds "
            f"(default: {SLOW_CALLBACK_DURATION})"
        ),
    )
    parser.add_argument(
        "--debug",
        "-d",
        action="store_true",
        default=get_eval(CVPA_DEBUG, False),
        help="Enable debugging mode and change logging severity to 'DEBUG'",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="count",
        default=get_eval(CVPA_VERBOSE, 0),
        help="Be more verbose/talkative during the operation",
    )
    parser.add_argument(
        "--version",
        "-V",
        action="version",
        version=version(),
    )
    parser.add_argument(
        "-D",
        action="store_true",
        default=False,
        help="Same as ['-c', '-d', '-vv'] flags",
    )

    subparsers = parser.add_subparsers(dest="cmd")
    add_agent_parser(subparsers)

    return parser


def _load_dotenv(
    cmdline: Optional[List[str]] = None,
    namespace: Optional[Namespace] = None,
) -> None:
    parser = ArgumentParser(add_help=False, allow_abbrev=False, exit_on_error=False)
    add_dotenv_arguments(parser)
    args = parser.parse_known_args(cmdline, namespace)[0]

    assert isinstance(args.no_dotenv, bool)
    assert isinstance(args.dotenv_path, str)

    if args.no_dotenv:
        return
    if not isfile(args.dotenv_path):
        return
    if not access(args.dotenv_path, R_OK):
        return

    try:
        from dotenv import load_dotenv

        load_dotenv(args.dotenv_path)
    except ModuleNotFoundError:
        pass


def _remove_dotenv_attrs(namespace: Namespace) -> Namespace:
    assert isinstance(namespace.no_dotenv, bool)
    assert isinstance(namespace.dotenv_path, str)

    del namespace.no_dotenv
    del namespace.dotenv_path

    assert not hasattr(namespace, "no_dotenv")
    assert not hasattr(namespace, "dotenv_path")

    return namespace


def _inject_default_subcommand(
    cmdline: Optional[List[str]],
) -> Optional[List[str]]:
    if cmdline is None:
        from sys import argv

        args_list = list(argv[1:])
    else:
        args_list = list(cmdline)

    if CMD_AGENT in args_list:
        return args_list

    for i, arg in enumerate(args_list):
        if arg.startswith(AGENT_TOKEN_PREFIX):
            args_list.insert(i, CMD_AGENT)
            return args_list

    return args_list


def get_default_arguments(
    cmdline: Optional[List[str]] = None,
    namespace: Optional[Namespace] = None,
) -> Namespace:
    # [IMPORTANT] Dotenv related options are processed first.
    _load_dotenv(cmdline, namespace)

    cmdline = _inject_default_subcommand(cmdline)

    parser = default_argument_parser()
    args = parser.parse_known_args(cmdline, namespace)[0]

    # Remove unnecessary dotenv attrs
    return _remove_dotenv_attrs(args)
