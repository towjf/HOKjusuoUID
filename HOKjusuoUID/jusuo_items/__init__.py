"""物品列表：菜地 + 牧场在售物品名清单（纯文本）。"""

from __future__ import annotations

from gsuid_core.bot import Bot
from gsuid_core.models import Event
from gsuid_core.sv import SV

from ..jusuo_config import api_kwargs
from ..utils.api import JusuoAPI, JusuoAPIError

sv = SV("HOKjusuoUID-物品列表", pm=6, priority=5)


@sv.on_command("物品列表", block=True, to_ai="列出菜地与牧场当前在售的全部物品名称")
async def cmd_item_list(bot: Bot, ev: Event) -> None:
    api = JusuoAPI(**api_kwargs())
    try:
        crops = await api.residence_entries(limit=500)
        ranch = await api.ranch_entries_with_names(limit=500)
    except JusuoAPIError as exc:
        await bot.send(f"居所助手取数失败：{exc}")
        return
    finally:
        await api.close()

    crop_names = sorted({e.get("crop_name") for e in crops if e.get("crop_name")})
    ranch_names = sorted({e.get("product_name") for e in ranch if e.get("product_name")})
    lines = [
        "【菜地】" + ("、".join(crop_names) if crop_names else "暂无"),
        "【牧场】" + ("、".join(ranch_names) if ranch_names else "暂无"),
    ]
    await bot.send("\n".join(lines))


__all__ = ["cmd_item_list", "sv"]
