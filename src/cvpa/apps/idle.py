# -*- coding: utf-8 -*-

from typing import Any

from cvpa.apps.base import App
from cvpa.runtime.context import RuntimeContext


class IdleApp(App):
    def start(self) -> None:
        raise RuntimeError("IdleApp requires --token for connected mode")

    async def run_async(self, ctx: Any) -> None:
        assert isinstance(ctx, RuntimeContext)
        await ctx.stop_event.wait()
