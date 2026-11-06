"""抓真实数据出一组 README 截图到 docs/images/（无损 WebP）。

用法（仓库根目录）：
    python tests/preview.py
"""

import asyncio
import sys
import types
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

# 只借用插件里的纯逻辑模块，绕开需要 gsuid_core 的 __init__.py
if "gs_jusuo" not in sys.modules:
    _pkg = types.ModuleType("gs_jusuo")
    _pkg.__path__ = [str(ROOT / "gs_jusuo")]  # type: ignore[attr-defined]
    sys.modules["gs_jusuo"] = _pkg

from gs_jusuo.jusuo_api import JusuoAPI  # noqa: E402
from gs_jusuo.jusuo_image import save_image  # noqa: E402
from gs_jusuo.jusuo_view import entry_card, market_card  # noqa: E402

OUT = ROOT / "docs" / "images"


async def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    api = JusuoAPI(cache_ttl=0)
    try:
        prices = await api.unit_prices()
        residence = await api.residence_entries()
        ranch = await api.ranch_entries_with_names()
        matrix = await api.market_matrix("crop", "price", 24)

        def make_card(entries, source, sort_mode):
            is_res = source == "residence"
            return entry_card(
                entries,
                prices,
                title="菜地 · 高倍收购" if is_res else "牧场 · 高倍收购",
                name_key="crop_name" if is_res else "product_name",
                level_key="residence_level" if is_res else "animal_stall_level",
                level_label="居所" if is_res else "摊位",
                price_category="crop" if is_res else "ranch",
                min_mult=None,
                min_level=None,
                page_size=10,
                page=1,
                sort_mode=sort_mode,
                hide_limited=True,
            )

        cards = {
            "residence-sale": make_card(residence, "residence", "sale"),
            "residence-unit": make_card(residence, "residence", "unit"),
            "ranch-sale": make_card(ranch, "ranch", "sale"),
            "market": market_card(
                matrix, source_label="菜地", metric="price", hours=24, limit=8
            ),
        }

        for name, card in cards.items():
            print(f"{name}: {save_image(card, OUT / (name + '.webp'))}")
    finally:
        await api.close()


if __name__ == "__main__":
    asyncio.run(main())
