"""居所助手 · gscore（早柚核心）插件。

数据来自玩家自发分享的 jusuo.playmmo.cn，直连其公开只读 Supabase 接口。
命令：菜地 / 牧场 / 物品列表 / 行情 / 居所帮助 / 居所状态
"""

from __future__ import annotations

import time

from gsuid_core.bot import Bot
from gsuid_core.logger import logger
from gsuid_core.models import Event
from gsuid_core.sv import Plugins, SV
from gsuid_core.utils.image.convert import convert_img

from .jusuo_api import JusuoAPI, JusuoAPIError
from .jusuo_config import api_kwargs, conf
from .jusuo_image import render_card
from .jusuo_params import parse_entries_args, tokens
from .jusuo_text import card_to_text
from .jusuo_view import entry_card, help_rows_card, market_card

__version__ = "1.0.1"

# 插件级配置：只允许空前缀（直接发「菜地」）。
# 这里【不要】写 force_prefix：gscore 会把每个命令按前缀展开成多份触发器，
# 填了「居所」之后控制台里每条命令都会出现「菜地」和「居所菜地」两条。
# 需要前缀时由部署者在插件配置里自行添加即可。
Plugins(name="gs_jusuo", allow_empty_prefix=True)

# 一个命令一个 SV：控制台里可以单独开关、单独调权限与优先级
sv_residence = SV("居所助手-菜地", pm=6, priority=5)
sv_ranch = SV("居所助手-牧场", pm=6, priority=5)
sv_items = SV("居所助手-物品列表", pm=6, priority=5)
sv_market = SV("居所助手-行情", pm=6, priority=5)
sv_help = SV("居所助手-命令帮助", pm=6, priority=5)
sv_status = SV("居所助手-自检", pm=1, priority=5)  # pm=1 → 仅超级管理员

HELP_ITEMS = [
    {
        "cmd": "菜地 [物品] [单价|售价] [页数]",
        "what": "菜地作物高倍收购",
        "how": "默认售价优先、第 1 页。例：菜地 草莓 / 菜地 草莓 单价 2",
    },
    {
        "cmd": "牧场 [物品] [单价|售价] [页数]",
        "what": "牧场动物产物收购",
        "how": "规则同菜地。例：牧场 羊毛 单价",
    },
    {
        "cmd": "物品列表",
        "what": "菜地 + 牧场的物品清单",
        "how": "把当前在售的作物与牧场产物名字全部列出来，只有名字",
    },
    {
        "cmd": "行情 [菜地|牧场] [小时]",
        "what": "近 N 小时行情峰值",
        "how": "默认菜地、24 小时。例：行情 牧场 48",
    },
    {
        "cmd": "居所状态",
        "what": "自检（仅超级管理员）",
        "how": "返回接口连通性、出图方式与插件版本",
    },
]

_render_log = logger


def _api() -> JusuoAPI:
    return JusuoAPI(**api_kwargs())


async def _send_card(bot: Bot, card: dict) -> None:
    """优先出图，失败退纯文本。"""
    if not conf("use_image"):
        await bot.send(card_to_text(card))
        return
    try:
        png = render_card(card)
        await bot.send(await convert_img(png))
    except Exception as exc:  # noqa: BLE001
        _render_log.exception(f"[居所助手] 出图失败，改用纯文本: {exc}")
        await bot.send(card_to_text(card))


# ---------------------------------------------------------------- 菜地 / 牧场


async def _entries_card(ev: Event, source: str):
    args = parse_entries_args(tokens(getattr(ev, "text", "") or ""))
    sort_mode = args.sort_mode or ("unit" if conf("default_sort") == "单价" else "sale")
    api = _api()

    try:
        if source == "residence":
            entries = await api.residence_entries(limit=int(conf("fetch_limit") or 300))
            prices = await api.unit_prices()
            return entry_card(
                entries,
                prices,
                title="菜地 · 高倍收购",
                name_key="crop_name",
                level_key="residence_level",
                level_label="居所",
                price_category="crop",
                min_mult=args.min_mult,
                min_level=args.min_level,
                page_size=int(conf("page_size") or 10),
                page=args.page,
                sort_mode=sort_mode,
                hide_limited=bool(conf("hide_limited")),
                item_keyword=args.item_keyword,
            )

        entries = await api.ranch_entries_with_names(
            limit=int(conf("fetch_limit") or 300)
        )
        prices = await api.unit_prices()
        return entry_card(
            entries,
            prices,
            title="牧场 · 高倍收购",
            name_key="product_name",
            level_key="animal_stall_level",
            level_label="摊位",
            price_category="ranch",
            min_mult=args.min_mult,
            min_level=args.min_level,
            page_size=int(conf("page_size") or 10),
            page=args.page,
            sort_mode=sort_mode,
            hide_limited=bool(conf("hide_limited")),
            item_keyword=args.item_keyword,
        )
    finally:
        await api.close()


@sv_residence.on_command(
    "菜地",
    block=True,
    to_ai="查询王者荣耀世界居所助手的菜地作物高倍收购列表，参数可为 物品名/单价|售价/页数",
)
async def cmd_residence(bot: Bot, ev: Event) -> None:
    try:
        card = await _entries_card(ev, "residence")
    except JusuoAPIError as exc:
        await bot.send(f"居所助手取数失败：{exc}")
        return
    await _send_card(bot, card)


@sv_ranch.on_command(
    "牧场",
    block=True,
    to_ai="查询王者荣耀世界居所助手的牧场动物产物高倍收购列表，参数可为 物品名/单价|售价/页数",
)
async def cmd_ranch(bot: Bot, ev: Event) -> None:
    try:
        card = await _entries_card(ev, "ranch")
    except JusuoAPIError as exc:
        await bot.send(f"居所助手取数失败：{exc}")
        return
    await _send_card(bot, card)


# ---------------------------------------------------------------- 物品列表


@sv_items.on_command("物品列表", block=True, to_ai="列出菜地与牧场当前在售的全部物品名称")
async def cmd_item_list(bot: Bot, ev: Event) -> None:
    api = _api()
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


# ---------------------------------------------------------------- 行情


@sv_market.on_command(
    "行情",
    block=True,
    to_ai="查询近 N 小时各物品的最高成交估价峰值，参数可为 菜地|牧场 和 小时数",
)
async def cmd_market(bot: Bot, ev: Event) -> None:
    source = "crop"
    hours = int(conf("market_hours") or 24)
    for token in tokens(getattr(ev, "text", "") or ""):
        if token in {"牧场", "ranch"}:
            source = "ranch"
        elif token in {"菜地", "crop"}:
            source = "crop"
        elif token.isdigit():
            hours = max(6, min(int(token), 168))

    api = _api()
    try:
        matrix = await api.market_matrix(source=source, metric="price", hours=hours)
    except JusuoAPIError as exc:
        await bot.send(f"居所助手取数失败：{exc}")
        return
    finally:
        await api.close()

    card = market_card(
        matrix,
        source_label="菜地" if source == "crop" else "牧场产物",
        metric="price",
        hours=hours,
        limit=int(conf("page_size") or 10),
    )
    await _send_card(bot, card)


# ---------------------------------------------------------------- 帮助 / 自检


@sv_help.on_command("居所帮助", block=True)
async def cmd_help(bot: Bot, ev: Event) -> None:
    if not conf("use_image"):
        lines = ["【居所助手 命令一览】"]
        for item in HELP_ITEMS:
            lines.append(f"{item['cmd']}\n  {item['what']} · {item['how']}")
        await bot.send("\n".join(lines))
        return
    card = help_rows_card(HELP_ITEMS, "命令可用空格跟参数，例：菜地 草莓 单价 2")
    await _send_card(bot, card)


@sv_status.on_command("居所状态", block=True)
async def cmd_status(bot: Bot, ev: Event) -> None:
    lines = ["【居所助手自检】"]
    started = time.perf_counter()
    api = _api()
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
