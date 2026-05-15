# -*- coding: utf-8 -*-

from asyncio.exceptions import CancelledError
from typing import TYPE_CHECKING

from cvpa.logging.loggers import logger

if TYPE_CHECKING:
    from cvpa.apps.base import App


class StandaloneRuntime:
    def execute(self, app: "App") -> int:
        try:
            app.start()
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
