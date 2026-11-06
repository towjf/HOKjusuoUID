"""菜地：作物高倍收购列表。"""

from __future__ import annotations

from gsuid_core.bot import Bot
from gsuid_core.models import Event
from gsuid_core.sv import SV

from ..utils.api import JusuoAPIError
from ..utils.entries import build_entries_card
from ..utils.sender import send_card

sv = SV("HOKjusuoUID-菜地", pm=6, priority=5)


@sv.on_command(
    "菜地",
    block=True,
    to_ai="查询王者荣耀世界居所助手的菜地作物高倍收购列表，参数可为 物品名/单价|售价/页数",
)
async def cmd_residence(bot: Bot, ev: Event) -> None:
    try:
        card = await build_entries_card(ev, "residence")
    except JusuoAPIError as exc:
        await bot.send(f"居所助手取数失败：{exc}")
        return
    await send_card(bot, card)


__all__ = ["cmd_residence", "sv"]
