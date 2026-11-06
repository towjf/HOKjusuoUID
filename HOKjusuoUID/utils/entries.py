"""菜地 / 牧场共用取数逻辑。"""

from __future__ import annotations

from gsuid_core.models import Event

from ..jusuo_config import api_kwargs, conf
from .api import JusuoAPI
from .params import parse_entries_args, tokens
from .view import entry_card


async def build_entries_card(ev: Event, source: str) -> dict:
    """source: residence（菜地） / ranch（牧场）。"""
    args = parse_entries_args(tokens(getattr(ev, "text", "") or ""))
    sort_mode = args.sort_mode or ("unit" if conf("default_sort") == "单价" else "sale")
    api = JusuoAPI(**api_kwargs())

    try:
        if source == "residence":
            entries = await api.residence_entries(limit=int(conf("fetch_limit") or 300))
            name_key, level_key, level_label, price_category = (
                "crop_name",
                "residence_level",
                "居所",
                "crop",
            )
            title = "菜地 · 高倍收购"
        else:
            entries = await api.ranch_entries_with_names(limit=int(conf("fetch_limit") or 300))
            name_key, level_key, level_label, price_category = (
                "product_name",
                "animal_stall_level",
                "摊位",
                "ranch",
            )
            title = "牧场 · 高倍收购"

        prices = await api.unit_prices()
    finally:
        await api.close()

    return entry_card(
        entries,
        prices,
        title=title,
        name_key=name_key,
        level_key=level_key,
        level_label=level_label,
        price_category=price_category,
        min_mult=args.min_mult,
        min_level=args.min_level,
        page_size=int(conf("page_size") or 10),
        page=args.page,
        sort_mode=sort_mode,
        hide_limited=bool(conf("hide_limited")),
        item_keyword=args.item_keyword,
    )
