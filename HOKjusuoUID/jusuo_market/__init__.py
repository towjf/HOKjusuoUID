"""行情：近 N 小时各物品最高成交估价峰值。"""

from __future__ import annotations

from gsuid_core.bot import Bot
from gsuid_core.models import Event
from gsuid_core.sv import SV

from ..jusuo_config import api_kwargs, conf
from ..utils.api import JusuoAPI, JusuoAPIError
from ..utils.params import parse_market_args, split_args
from ..utils.sender import send_card
from ..utils.view import market_card

sv = SV("HOKjusuoUID-行情", pm=6, priority=5)


@sv.on_command(
    "行情",
    block=True,
    to_ai="查询近 N 小时各物品的最高成交估价峰值，参数可为 菜地|牧场 和 小时数",
)
async def cmd_market(bot: Bot, ev: Event) -> None:
    # 必须用 split_args：ev.text 已经不含命令词，若用 tokens() 会把「牧场」当命令词吃掉
    args = parse_market_args(
        split_args(getattr(ev, "text", "") or ""),
        default_hours=int(conf("market_hours") or 24),
    )

    api = JusuoAPI(**api_kwargs())
    try:
        matrix = await api.market_matrix(source=args.source, metric="price", hours=args.hours)
    except JusuoAPIError as exc:
        await bot.send(f"居所助手取数失败：{exc}")
        return
    finally:
        await api.close()

    card = market_card(
        matrix,
        source_label="菜地" if args.source == "crop" else "牧场产物",
        metric="price",
        hours=args.hours,
        limit=int(conf("page_size") or 10),
    )
    await send_card(bot, card)


__all__ = ["cmd_market", "sv"]
