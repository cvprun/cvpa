# -*- coding: utf-8 -*-

from argparse import Namespace

from cvpa.apps.base import App
from cvpa.apps.idle import IdleApp
from cvpa.apps.infer import build_infer_app
from cvpa.apps.train import build_train_app
from cvpa.arguments import CMD_AGENT, CMD_INFER, CMD_TRAIN
from cvpa.credentials.token import parse_agent_token
from cvpa.logging.loggers import logger
from cvpa.runtime.connected import ConnectedRuntime
from cvpa.runtime.standalone import StandaloneRuntime


def build_app(cmd: str, args: Namespace) -> App:
    if cmd == CMD_INFER:
        return build_infer_app(args)
    if cmd == CMD_TRAIN:
        return build_train_app(args)
    if cmd == CMD_AGENT:
        return IdleApp()
    raise ValueError(f"Unsupported app command: {cmd}")


def run_app(cmd: str, args: Namespace) -> int:
    try:
        app = build_app(cmd, args)
    except ValueError as e:
        logger.error(str(e))
        return 1

    if args.token:
        slug, token = parse_agent_token(args.token)
        runtime = ConnectedRuntime(
            uri=args.uri,
            slug=slug,
            token=token,
            use_uvloop=args.use_uvloop,
            debug=args.debug,
            slow_callback_duration=args.slow_callback_duration,
        )
        return runtime.execute(app)

    return StandaloneRuntime().execute(app)
