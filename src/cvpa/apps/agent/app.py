# -*- coding: utf-8 -*-

from asyncio import get_running_loop

from cvpa.aio.run import aio_run
from cvpa.apps.agent.ws_client import AgentWebSocketClient
from cvpa.logging.loggers import agent_logger as logger
from cvpa.variables import LOGGING_STEP, SLOW_CALLBACK_DURATION


class AgentApplication:
    def __init__(
        self,
        uri: str,
        slug: str,
        token: str,
        logging_step=LOGGING_STEP,
        slow_callback_duration=SLOW_CALLBACK_DURATION,
        use_uvloop=False,
        debug=False,
        verbose=0,
    ):
        self._uri = uri
        self._slug = slug
        self._token = token
        self._logging_step = logging_step
        self._slow_callback_duration = slow_callback_duration
        self._use_uvloop = use_uvloop
        self._debug = debug
        self._verbose = verbose
        self._ws_client = AgentWebSocketClient(uri, slug, token)

    async def on_main(self) -> None:
        logger.info(f"Starting agent application: {self._uri}")

        loop = get_running_loop()
        loop.slow_callback_duration = self._slow_callback_duration
        loop.set_debug(self._debug)

        try:
            await self._ws_client.start()
        except Exception as e:
            logger.error(f"Agent runtime error: {e}")
            raise
        finally:
            await self._ws_client.stop()
            logger.info("Agent application stopped")

    def start(self) -> None:
        try:
            aio_run(self.on_main(), self._use_uvloop)
        except KeyboardInterrupt, InterruptedError:
            logger.warning("Interrupt signal detected")
