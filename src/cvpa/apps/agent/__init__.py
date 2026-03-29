# -*- coding: utf-8 -*-

from argparse import Namespace

from cvpa.logging.loggers import agent_logger as logger
from cvpa.logging.logging import (
    SEVERITY_NAME_DEBUG,
    SEVERITY_NAME_WARNING,
    add_default_colored_logging,
    add_simple_logging,
    convert_level_number,
    set_asyncio_level,
)
from cvpa.variables import SLOW_CALLBACK_DURATION


def agent_main(args: Namespace) -> None:
    assert isinstance(args.uri, str)
    assert isinstance(args.slug, str)
    assert isinstance(args.token, str)
    assert isinstance(args.colored_logging, bool)
    assert isinstance(args.simple_logging, bool)
    assert isinstance(args.logging_step, int)
    assert isinstance(args.logging_severity, str)
    assert isinstance(args.use_uvloop, bool)
    assert isinstance(args.debug, bool)
    assert isinstance(args.verbose, int)
    assert isinstance(args.D, bool)
    assert isinstance(args.opts, list)

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

    # [IMPORTANT]
    # Do not change the import order!
    from cvpa.apps.agent.app import AgentApplication

    app = AgentApplication(
        uri=args.uri,
        slug=args.slug,
        token=args.token,
        logging_step=args.logging_step,
        slow_callback_duration=SLOW_CALLBACK_DURATION,
        use_uvloop=args.use_uvloop,
        debug=args.debug,
        verbose=args.verbose,
    )
    app.start()
