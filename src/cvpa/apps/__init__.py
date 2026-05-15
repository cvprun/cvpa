# -*- coding: utf-8 -*-

from argparse import Namespace
from asyncio.exceptions import CancelledError
from functools import lru_cache
from typing import Callable, Dict

from cvpa.apps.agent import agent_main
from cvpa.apps.base import App
from cvpa.apps.infer import build_infer_app, infer_main
from cvpa.apps.train import build_train_app, train_main
from cvpa.arguments import CMD_AGENT, CMD_INFER, CMD_TRAIN
from cvpa.credentials.token import parse_agent_token
from cvpa.logging.loggers import logger
from cvpa.runtime.connected import ConnectedRuntime
from cvpa.runtime.standalone import StandaloneRuntime


@lru_cache
def cmd_apps() -> Dict[str, Callable[[Namespace], None]]:
    return {
        CMD_AGENT: agent_main,
        CMD_TRAIN: train_main,
        CMD_INFER: infer_main,
    }


def build_app(cmd: str, args: Namespace) -> App:
    if cmd == CMD_INFER:
        return build_infer_app(args)
    if cmd == CMD_TRAIN:
        return build_train_app(args)
    raise ValueError(f"Unsupported app command: {cmd}")


def _run_legacy(cmd: str, args: Namespace) -> int:
    apps = cmd_apps()
    main = apps.get(cmd, None)
    if main is None:
        logger.error(f"Unknown app command: {cmd}")
        return 1

    try:
        main(args)
    except CancelledError:
        logger.debug("An cancelled signal was detected")
    except (KeyboardInterrupt, InterruptedError):
        logger.warning("An interrupt signal was detected")
    except SystemExit as e:
        assert isinstance(e.code, int)
        if e.code != 0:
            logger.warning(f"A system shutdown has been detected ({e.code})")
        return e.code
    except BaseException as e:
        logger.exception(e)
        return 1

    return 0


def run_app(cmd: str, args: Namespace) -> int:
    if cmd not in (CMD_INFER, CMD_TRAIN):
        return _run_legacy(cmd, args)

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
