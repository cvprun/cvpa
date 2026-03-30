# -*- coding: utf-8 -*-

from sys import exit as sys_exit
from typing import List, Optional

from cvpa.apps import run_app
from cvpa.arguments import get_default_arguments
from cvpa.logging.loggers import agent_logger as logger
from cvpa.logging.logging import (
    SEVERITY_NAME_DEBUG,
    SEVERITY_NAME_WARNING,
    add_default_colored_logging,
    add_simple_logging,
    convert_level_number,
    set_asyncio_level,
)


def main(cmdline: Optional[List[str]] = None) -> int:
    args = get_default_arguments(cmdline)

    assert isinstance(args.colored_logging, bool)
    assert isinstance(args.simple_logging, bool)
    assert isinstance(args.logging_step, int)
    assert isinstance(args.logging_severity, str)
    assert isinstance(args.use_uvloop, bool)
    assert isinstance(args.slow_callback_duration, float)
    assert isinstance(args.debug, bool)
    assert isinstance(args.verbose, int)
    assert isinstance(args.D, bool)

    if args.D:
        args.colored_logging = True
        args.simple_logging = False
        args.debug = True
        args.verbose = 2

    if args.debug:
        args.logging_severity = SEVERITY_NAME_DEBUG

    level = convert_level_number(args.logging_severity)
    logger.setLevel(level)

    if args.colored_logging:
        assert not args.simple_logging
        add_default_colored_logging(logger.name)
    elif args.simple_logging:
        assert not args.colored_logging
        add_simple_logging(logger.name)

    asyncio_severity = SEVERITY_NAME_DEBUG if args.debug else SEVERITY_NAME_WARNING
    asyncio_level = convert_level_number(asyncio_severity)
    set_asyncio_level(asyncio_level)

    return run_app(args.cmd, args)


if __name__ == "__main__":
    sys_exit(main())
