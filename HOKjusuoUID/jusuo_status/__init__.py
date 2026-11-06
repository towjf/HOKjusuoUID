"""状态：自检（仅超级管理员）。"""

from __future__ import annotations

import time

from gsuid_core.bot import Bot
from gsuid_core.models import Event
from gsuid_core.sv import SV

from ..jusuo_config import api_kwargs, conf
from ..utils.api import JusuoAPI
from ..version import __version__

sv = SV("HOKjusuoUID-状态", pm=1, priority=5)


@sv.on_command("状态", block=True)
async def cmd_status(bot: Bot, ev: Event) -> None:
    lines = ["【居所助手自检】"]
    started = time.perf_counter()
    api = JusuoAPI(**api_kwargs())
    try:
        entries = await api.residence_entries(limit=5)
        cost = (time.perf_counter() - started) * 1000
        lines.append(f"数据接口：正常（样本 {len(entries)} 条，{cost:.0f}ms）")
    except Exception as exc:  # noqa: BLE001
        lines.append(f"数据接口：失败 —— {exc}")
    finally:
        await api.close()

    lines.append(
        "出图方式：本地 Pillow 绘制"
        if conf("use_image")
        else "出图方式：纯文本（配置里关闭了 use_image）"
    )
    lines.append(f"插件版本：v{__version__}")
    await bot.send("\n".join(lines))


__all__ = ["cmd_status", "sv"]
