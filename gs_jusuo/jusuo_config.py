"""插件配置（持久化到 gsuid_core/data/gs_jusuo/config.json，可在网页控制台修改）。"""

from __future__ import annotations

from typing import Dict

from gsuid_core.data_store import get_res_path
from gsuid_core.utils.plugins_config.gs_config import StringConfig
from gsuid_core.utils.plugins_config.models import (
    GSC,
    GsBoolConfig,
    GsDivider,
    GsIntConfig,
    GsStrConfig,
)

from .jusuo_api import DEFAULT_ANON_KEY, DEFAULT_BASE_URL

CONFIG_PATH = get_res_path("gs_jusuo") / "config.json"

JUSUO_CONFIG_DEFAULT: Dict[str, GSC] = {
    "接口": GsDivider(title="接口", desc="", data=None),
    "supabase_url": GsStrConfig(
        "数据接口地址", "站点使用的 Supabase 地址，一般不用改", DEFAULT_BASE_URL
    ),
    "anon_key": GsStrConfig(
        "接口 anon key",
        "站点前端内置的公开只读 key，留空则使用插件内置值",
        "",
    ),
    "timeout": GsIntConfig("请求超时（秒）", "单次 HTTP 请求的超时时间", 15, max_value=60),
    "cache_ttl": GsIntConfig(
        "基础数据缓存（秒）", "单价表、牧场产物名等静态数据的缓存时长，0 表示不缓存", 90
    ),
    "查询": GsDivider(title="查询", desc="", data=None),
    "default_sort": GsStrConfig(
        "默认排序",
        "菜地/牧场不带参数时的排序方式",
        "售价",
        options=["售价", "单价"],
    ),
    "page_size": GsIntConfig("每页条数", "图片里每页显示多少条", 10, max_value=20),
    "hide_limited": GsBoolConfig("排除已限购", "开启后不再显示商家已经抢光的记录", True),
    "fetch_limit": GsIntConfig("单次拉取条数", "从接口拉多少条后再筛选，越大越全但越慢", 300),
    "出图": GsDivider(title="出图", desc="", data=None),
    "use_image": GsBoolConfig("输出图片卡片", "关闭后直接输出纯文本", True),
    "market_hours": GsIntConfig("行情默认小时数", "行情命令不带小时参数时的默认值", 24, max_value=168),
}

jusuo_config = StringConfig("gs_jusuo", CONFIG_PATH, JUSUO_CONFIG_DEFAULT)


def conf(key: str):
    """取配置项的 .data。"""
    return jusuo_config.get_config(key).data


def api_kwargs() -> dict:
    """给 JusuoAPI 用的参数集合。"""
    return {
        "base_url": conf("supabase_url") or DEFAULT_BASE_URL,
        "anon_key": conf("anon_key") or DEFAULT_ANON_KEY,
        "timeout": float(conf("timeout") or 15),
        "cache_ttl": int(conf("cache_ttl") or 0),
    }
