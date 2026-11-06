"""帮助：命令一览（出图）。"""

from __future__ import annotations

from gsuid_core.bot import Bot
from gsuid_core.models import Event
from gsuid_core.sv import SV

from ..jusuo_config import conf
from ..utils.sender import send_card
from ..utils.view import help_rows_card

sv = SV("HOKjusuoUID-帮助", pm=6, priority=5)

HELP_ITEMS = [
    {
        "cmd": "js菜地 [物品] [单价|售价] [页数]",
        "what": "菜地作物高倍收购",
        "how": "默认售价优先、第 1 页。例：js菜地 草莓 / js菜地 草莓 单价 2",
    },
    {
        "cmd": "js牧场 [物品] [单价|售价] [页数]",
        "what": "牧场动物产物收购",
        "how": "规则同菜地。例：js牧场 羊毛 单价",
    },
    {
        "cmd": "js物品列表",
        "what": "菜地 + 牧场的物品清单",
        "how": "把当前在售的作物与牧场产物名字全部列出来，只有名字",
    },
    {
        "cmd": "js行情 [菜地|牧场] [小时]",
        "what": "近 N 小时行情峰值",
        "how": "默认菜地、24 小时。例：js行情 牧场 48",
    },
    {
        "cmd": "js状态",
        "what": "自检（仅超级管理员）",
        "how": "返回接口连通性、出图方式与插件版本",
    },
]

SUBTITLE = "命令必须带前缀 js 或 居所，例：js菜地 草莓 单价 2"


@sv.on_command("帮助", block=True)
async def cmd_help(bot: Bot, ev: Event) -> None:
    if not conf("use_image"):
        lines = ["【居所助手 命令一览】", SUBTITLE]
        for item in HELP_ITEMS:
            lines.append(f"{item['cmd']}\n  {item['what']} · {item['how']}")
        await bot.send("\n".join(lines))
        return
    await send_card(bot, help_rows_card(HELP_ITEMS, SUBTITLE))


__all__ = ["HELP_ITEMS", "cmd_help", "sv"]
