# -*- coding: utf-8 -*-

import asyncio
from asyncio import create_task, get_running_loop
from typing import TYPE_CHECKING

from cvpa.aio.run import aio_run
from cvpa.logging.loggers import agent_logger as logger
from cvpa.runtime.context import RuntimeContext
from cvpa.variables import SLOW_CALLBACK_DURATION
from cvpa.ws.connection import AgentConnection

if TYPE_CHECKING:
    from cvpa.apps.base import App


class ConnectedRuntime:
    def __init__(
        self,
        uri: str,
        slug: str,
        token: str,
        *,
        use_uvloop: bool = False,
        debug: bool = False,
        slow_callback_duration: float = SLOW_CALLBACK_DURATION,
        agent_version: str = "",
    ) -> None:
        self._uri = uri
        self._slug = slug
        self._token = token
        self._use_uvloop = use_uvloop
        self._debug = debug
        self._slow_callback_duration = slow_callback_duration
        self._agent_version = agent_version

    def execute(self, app: "App") -> int:
        try:
            aio_run(self._run(app), self._use_uvloop)
        except (KeyboardInterrupt, InterruptedError):
            logger.warning("Interrupt signal detected")
            return 1
        except BaseException as e:
            logger.exception(e)
            return 1
        return 0

    async def _run(self, app: "App") -> None:
        loop = get_running_loop()
        loop.slow_callback_duration = self._slow_callback_duration
        loop.set_debug(self._debug)

        dispatcher = app.build_dispatcher(logger=logger)
        connection = AgentConnection(
            uri=self._uri,
            slug=self._slug,
            token=self._token,
            dispatcher=dispatcher,
            logger=logger,
            agent_version=self._agent_version,
        )
        app.bind_sender(connection.send_envelope)

        ctx = RuntimeContext()

        connection_task = create_task(connection.start())
        app_task = create_task(app.run_async(ctx))

        try:
            _, pending = await asyncio.wait(
                {connection_task, app_task},
                return_when=asyncio.FIRST_COMPLETED,
            )
            ctx.stop_event.set()
            for task in pending:
                task.cancel()
            for task in pending:
                try:
                    await task
                except asyncio.CancelledError:
                    pass
                except Exception as e:
                    logger.exception(e)
        finally:
            await connection.stop()
            logger.info("Connected runtime stopped")
