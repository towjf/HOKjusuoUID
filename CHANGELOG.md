# 更新日志

## 1.1.0

### 变更

- 插件改名 `HOKjusuoUID`（仓库名、目录名、`Plugins(name=...)`、SV 名、配置目录同步），符合 `GenshinUID` / `StarRailUID` 这类「游戏缩写 + UID」的命名惯例；
- 发布包改为双形态：`HOKjusuoUID-flat.zip`（根层直接放 `__init__.py`，供控制台上传安装）与 `HOKjusuoUID.zip`（根层是 `HOKjusuoUID/` 文件夹，供手动解压）；

## 1.0.1

### 变更

- 每个命令拆成独立的 SV（`居所助手-菜地` / `-牧场` / `-物品列表` / `-行情` / `-命令帮助` / `-自检`），可在控制台单独开关、设权限与优先级；
- `居所状态` 权限改为 `pm=1`（仅超级管理员）；
- 去掉 `Plugins(force_prefix=["居所"])`：该参数会让 gscore 把每个命令按前缀展开成两份触发器，控制台里每条命令重复显示两次；
- 去掉 `居所状态` 的 `aliases`（gscore 的 aliases 只用于 AI 工具注册，不会生成聊天触发器）。

## 1.0.0

首个 gscore 版本，与 AstrBot 版 `astrbot_plugin_jusuo` v1.5.0 功能对齐。

### 功能

- `菜地` / `牧场`：高倍收购列表，支持物品筛选、单价/售价排序、翻页，带商人 UID、等级、剩余时间与整批预计售价；
- `物品列表`：菜地 + 牧场在售物品名清单；
- `行情`：近 N 小时各物品最高成交估价峰值；
- `居所帮助` / `居所状态`：命令图与自检；
- 本地 Pillow 出图（960px 宽、深蓝配色），失败自动退纯文本；
- 命令带 `to_ai` 描述，可被 gscore AI Core 直接调用。

### 适配

- 使用 httpx 打 Supabase REST 接口，代理环境异常（如 `NO_PROXY` 含 `[::1]`）时自动退回不读环境变量；
- 配置项接入网页控制台，写入 `gsuid_core/data/HOKjusuoUID/config.json`；
- 插件级前缀：默认允许无前缀，同时注册 `居所` 前缀。

### 测试

- 15 个单元测试（参数解析、格式化、视图、绘制），不依赖 gscore；
- `tests/smoke_test.py` 用自带的 gsuid_core 桩跑通全部命令。
