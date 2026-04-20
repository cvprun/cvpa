# -*- coding: utf-8 -*-

from argparse import Namespace

from cvpa.apps.agent.token import parse_agent_token


def agent_main(args: Namespace) -> None:
    assert isinstance(args.logging_step, int)
    assert isinstance(args.use_uvloop, bool)
    assert isinstance(args.slow_callback_duration, float)
    assert isinstance(args.debug, bool)
    assert isinstance(args.verbose, int)
    assert isinstance(args.uri, str)
    assert isinstance(args.token, str)
    assert isinstance(getattr(args, "legacy_protocol", False), bool)

    slug, token = parse_agent_token(args.token)

    # [IMPORTANT]
    # Do not change the import order!
    from cvpa.apps.agent.app import AgentApplication

    app = AgentApplication(
        uri=args.uri,
        slug=slug,
        token=token,
        logging_step=args.logging_step,
        slow_callback_duration=args.slow_callback_duration,
        use_uvloop=args.use_uvloop,
        debug=args.debug,
        verbose=args.verbose,
        legacy_protocol=getattr(args, "legacy_protocol", False),
    )
    app.start()
