"""HOKjusuoUID · 居所助手 · gscore（早柚核心）插件。

数据来自玩家自发分享的 jusuo.playmmo.cn，直连其公开只读 Supabase 接口。

目录结构（参考 EndUID 的分包约定）：
    __init__.py       仅做插件注册与子包导入
    version.py        版本号
    jusuo_config.py   网页控制台配置
    jusuo_residence/  菜地
    jusuo_ranch/      牧场
    jusuo_items/      物品列表
    jusuo_market/     行情
    jusuo_help/       帮助
    jusuo_status/     状态（仅超级管理员）
    utils/            接口、参数、视图、绘制、发送
"""

from __future__ import annotations

from gsuid_core.sv import Plugins

from .version import __version__

# 插件级配置必须写在导入子包之前：子包里的 SV() 会按插件名查前缀配置
# 默认前缀 js / 居所，allow_empty_prefix=False → 不存在裸命令
Plugins(
    name="HOKjusuoUID",
    prefix=["js", "居所"],
    allow_empty_prefix=False,
)

from . import (  # noqa: E402,F401  导入即注册命令
    jusuo_help,
    jusuo_items,
    jusuo_market,
    jusuo_ranch,
    jusuo_residence,
    jusuo_status,
)

__all__ = ["__version__"]
