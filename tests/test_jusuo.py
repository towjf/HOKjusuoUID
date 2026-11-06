"""参数 / 格式化 / 视图 / 绘制 的单测。

不依赖 gsuid_core：这里给插件包做一个空壳，直接导入其中的纯逻辑模块，
因此可以在任何装了 Pillow 的环境里跑 `python -m unittest`。
"""

import io
import sys
import types
import unittest
from datetime import UTC, datetime, timedelta
from pathlib import Path

from PIL import Image

PLUGIN_DIR = Path(__file__).resolve().parents[1] / "gs_jusuo"
sys.path.insert(0, str(PLUGIN_DIR.parent))

if "gs_jusuo" not in sys.modules:
    _pkg = types.ModuleType("gs_jusuo")
    _pkg.__path__ = [str(PLUGIN_DIR)]  # type: ignore[attr-defined]
    sys.modules["gs_jusuo"] = _pkg

from gs_jusuo.jusuo_format import (  # noqa: E402
    estimate_price,
    fmt_money,
    fmt_remaining,
    multiplier_tone,
)
from gs_jusuo.jusuo_image import render_card  # noqa: E402
from gs_jusuo.jusuo_params import parse_entries_args, tokens  # noqa: E402
from gs_jusuo.jusuo_text import card_to_text  # noqa: E402
from gs_jusuo.jusuo_view import entry_card  # noqa: E402

PRICES = {"crop": {"荆棘草莓": 460.0}, "ranch": {"浅滩羊驼毛": 800.0}}
FAR_FUTURE = (datetime.now(UTC) + timedelta(days=3)).isoformat()


def make_entry(uid="131809", quantity=2880, multiplier=1.9, level=78, limited=False):
    return {
        "crop_name": "荆棘草莓",
        "quantity": quantity,
        "price_multiplier": multiplier,
        "merchant_name": "金糜(工巧家)",
        "residence_level": level,
        "expires_at": FAR_FUTURE,
        "is_limit_reached": limited,
        "guild_maxed": True,
        "sale_price": None,
        "uid": uid,
    }


def build(entries, **kwargs):
    options = dict(
        title="菜地 · 高倍收购",
        name_key="crop_name",
        level_key="residence_level",
        level_label="居所",
        price_category="crop",
        min_mult=None,
        min_level=None,
        page_size=10,
        page=1,
        sort_mode="sale",
        hide_limited=True,
    )
    options.update(kwargs)
    return entry_card(entries, PRICES, **options)


class TestParams(unittest.TestCase):
    def test_tokens_strip_command(self):
        self.assertEqual(tokens("菜地 草莓 单价 2"), ["草莓", "单价", "2"])
        self.assertEqual(tokens(""), [])

    def test_combined_args(self):
        args = parse_entries_args(["草莓", "单价", "2"])
        self.assertEqual(args.item_keyword, "草莓")
        self.assertEqual(args.sort_mode, "unit")
        self.assertEqual(args.page, 2)

    def test_filters(self):
        args = parse_entries_args(["倍率2", "等级70"])
        self.assertEqual(args.min_mult, 2.0)
        self.assertEqual(args.min_level, 70)

    def test_page_clamped(self):
        self.assertEqual(parse_entries_args(["0"]).page, 1)


class TestFormat(unittest.TestCase):
    def test_money(self):
        self.assertEqual(fmt_money(15_580_000), "1558万")
        self.assertEqual(fmt_money(10_000), "1万")
        self.assertEqual(fmt_money(123_456_789), "1.23亿")

    def test_remaining(self):
        now = datetime(2026, 11, 6, tzinfo=UTC)
        future = (now + timedelta(hours=5, minutes=12)).isoformat()
        self.assertEqual(fmt_remaining(future, now), "5时12分")
        self.assertEqual(fmt_remaining(None, now), "-")

    def test_estimate_price(self):
        expected = round(460 * (1 + (78 * 5 - 5) / 100) * 1.9 * 2880 * 1.2)
        self.assertEqual(estimate_price(460, 78, 1.9, 2880, True), expected)
        self.assertIsNone(estimate_price(None, 78, 1.9, 2880, False))

    def test_tone(self):
        self.assertEqual(multiplier_tone(2.0), "gold")
        self.assertEqual(multiplier_tone(1.2), "green")


class TestView(unittest.TestCase):
    def test_sort_and_paging(self):
        entries = [make_entry(uid=f"u{i}", quantity=1000 + i * 10) for i in range(15)]
        card = build(entries, page=2, page_size=10)
        self.assertEqual(len(card["rows"]), 5)
        self.assertEqual(card["rows"][0]["rank"], 11)
        self.assertIn("第 2/2 页", [c["text"] for c in card["chips"]])

    def test_unit_sort(self):
        # 单价 = 整批总价 / 数量；等级更高的小批量条目每件更贵
        entries = [
            make_entry(uid="low-per-item", quantity=2880, level=60),
            make_entry(uid="high-per-item", quantity=1000, level=79),
        ]
        card = build(entries, sort_mode="unit")
        self.assertEqual(card["rows"][0]["uid"], "high-per-item")

    def test_keyword_and_limited(self):
        entries = [make_entry(uid="ok"), make_entry(uid="lim", limited=True)]
        self.assertEqual(len(build(entries)["rows"]), 1)
        card = build(entries, hide_limited=False, item_keyword="草莓")
        self.assertEqual(len(card["rows"]), 2)

    def test_uid_in_row(self):
        card = build([make_entry()])
        self.assertEqual(card["rows"][0]["uid"], "131809")
        self.assertEqual(card["footer"], "数据来源jusuo.playmmo.cn")
        self.assertEqual(card["source"], "禁鬼有型&居所助手")

    def test_empty_state(self):
        card = build([], min_mult=9)
        self.assertEqual(card["rows"], [])


class TestRender(unittest.TestCase):
    def test_png(self):
        data = render_card(build([make_entry()]))
        self.assertTrue(data.startswith(b"\x89PNG"))
        image = Image.open(io.BytesIO(data))
        self.assertEqual(image.width, 960)
        self.assertGreater(image.height, 300)

    def test_text_fallback(self):
        text = card_to_text(build([make_entry()]))
        self.assertIn("UID：131809", text)
        self.assertIn("荆棘草莓", text)
        self.assertIn("数据来源jusuo.playmmo.cn", text)


if __name__ == "__main__":
    unittest.main()
