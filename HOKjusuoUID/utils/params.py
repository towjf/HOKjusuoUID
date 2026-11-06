"""命令行参数解析（纯字符串处理，不依赖 AstrBot，便于单元测试）。"""

from __future__ import annotations

import re
from typing import NamedTuple

SLASHES = ("/", "／")
"""命令触发用的斜杠：半角与全角。"""

_LEVEL_PATTERN = re.compile(r"^[Ll][Vv]?\d+$")

COMMAND_WORDS = (
    "菜地",
    "牧场",
    "行情",
    "物品列表",
    "居所帮助",
    "居所测试",
)
"""命令首词，用于把整条原文（"/菜地 草莓 单价" 或 "菜地 草莓 单价"）还原成参数列表。

注意：gscore 的 `ev.text` 已经去掉了命令词，解析 `ev.text` 时请用 `split_args()`，
否则像 `行情 牧场` 里的「牧场」会被当成命令词吃掉。
"""

MARKET_CROP = {"菜地", "作物", "crop"}
MARKET_RANCH = {"牧场", "产物", "ranch"}

SORT_UNIT = {"单价", "单件", "单价优先", "unit"}
SORT_SALE = {"售价", "总价", "售价优先", "sale"}


class EntriesArgs(NamedTuple):
    """`/菜地`、`/牧场` 的解析结果。"""

    item_keyword: str
    """物品关键词，空字符串表示不过滤。"""

    sort_mode: str | None
    """`unit` 单价优先 / `sale` 售价优先 / None 表示用配置里的默认值。"""

    page: int
    """页码，从 1 开始。"""

    min_mult: float | None
    """最低倍率，None 表示不过滤。"""

    min_level: int | None
    """最低等级，None 表示不过滤。"""


class MarketArgs(NamedTuple):
    """`行情` 的解析结果。"""

    source: str
    """`crop` 菜地 / `ranch` 牧场。"""

    hours: int
    """统计窗口小时数。"""


def has_slash(raw_text: str | None) -> bool:
    """判断用户原始消息是否以斜杠开头（拿不到原文时不拦截）。"""
    if raw_text is None:
        return True
    text = str(raw_text).strip()
    if not text:
        return True
    return text.startswith(SLASHES)


def split_args(message_str: str | None) -> list[str]:
    """把「命令之后的文本」切成参数列表。

    不做命令词剥离：gscore 传进来的 `ev.text` 本来就不含命令词，
    这样 `行情 牧场` 的「牧场」才不会被误删。
    """
    text = str(message_str or "").replace("　", " ").strip()
    text = text.lstrip("".join(SLASHES)).strip()
    return [part for part in text.split() if part]


def tokens(message_str: str | None) -> list[str]:
    """从**整条原文**里取出参数（会剥掉首词命令）。

    只在拿得到 `raw_text` 的场景使用；解析 `ev.text` 请用 `split_args()`。
    """
    parts = split_args(message_str)
    if parts and parts[0] in COMMAND_WORDS:
        parts = parts[1:]
    return parts


def parse_market_args(argv: list[str], *, default_hours: int = 24) -> MarketArgs:
    """解析 `行情` 的参数。

    支持的写法：
        行情                 → 菜地，默认小时数
        行情 牧场            → 牧场产物
        行情 菜地 48         → 菜地，近 48 小时
        行情 牧场 6          → 牧场，近 6 小时（小时数限定 6~168）
    """
    source = "crop"
    hours = default_hours
    for raw in argv:
        token = str(raw).strip()
        if not token:
            continue
        low = token.lower()
        if low in MARKET_RANCH:
            source = "ranch"
        elif low in MARKET_CROP:
            source = "crop"
        elif token.isdigit():
            hours = max(6, min(int(token), 168))
    return MarketArgs(source, hours)


def parse_entries_args(argv: list[str]) -> EntriesArgs:
    """解析 `/菜地`、`/牧场` 的参数。

    支持的写法：
        /菜地                     → 全部物品，售价优先，第 1 页
        /菜地 草莓                 → 只看名字含「草莓」的
        /菜地 草莓 单价            → 单价优先
        /菜地 草莓 售价 2          → 售价优先第 2 页
        /菜地 倍率2 等级70 售价     → 附带过滤条件（可选）
    """
    sort_mode: str | None = None
    page = 1
    min_mult: float | None = None
    min_level: int | None = None
    words: list[str] = []

    for token in argv:
        text = str(token).strip()
        if not text:
            continue
        low = text.lower()

        if low in SORT_UNIT:
            sort_mode = "unit"
            continue
        if low in SORT_SALE:
            sort_mode = "sale"
            continue
        if text.startswith(("倍率", "×")):
            try:
                min_mult = float(text.lstrip("倍率×xX"))
            except ValueError:
                pass
            continue
        if text.startswith("等级"):
            digits = "".join(ch for ch in text if ch.isdigit())
            if digits:
                min_level = int(digits)
            continue
        if _LEVEL_PATTERN.match(text):
            min_level = int(text.lstrip("LlVv"))
            continue
        if text.endswith(("x", "X", "倍")) and text[:-1].replace(".", "").isdigit():
            try:
                min_mult = float(text.rstrip("xX倍"))
            except ValueError:
                pass
            continue
        if text.isdigit():
            page = max(1, int(text))
            continue
        words.append(text)

    return EntriesArgs(" ".join(words).strip(), sort_mode, page, min_mult, min_level)
