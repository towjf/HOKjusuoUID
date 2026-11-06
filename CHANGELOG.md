# 更新日志

## 1.3.2

### 修复

- **`js行情 牧场` 一直显示菜地数据**：`utils.params.tokens()` 会把首词命令（含「牧场」「菜地」「行情」）
  当命令词剥掉，而 gscore 传进来的 `ev.text` 本来就不含命令词，于是参数里的「牧场」被吃掉，
  `source` 永远停在默认的 `crop`；
  新增 `split_args()`（只切词、不剥命令词）与纯函数 `parse_market_args()`，
  行情命令改用两者，`菜地`/`牧场`/`小时数` 解析全部走单测覆盖。
- 同类隐患一并修掉：`菜地`/`牧场` 的参数解析也从 `tokens()` 换成 `split_args()`。
- `tokens()` 保留但标注为「只能喂整条原文（含命令词）」。

## 1.3.1

### 变更

- 前缀改走插件级「强制前缀」，与 EndUID（`end` / `zmd`）等插件保持一致：
  `Plugins(prefix=[], force_prefix=["js", "居所"], allow_empty_prefix=False)`；
- 控制台「插件服务配置」里表现为：默认前缀=关闭、强制前缀=`js, 居所`、允许空前缀=关；
- 强制前缀不写入 `data/plugins_config/HOKjusuoUID.json`，部署者不会误删；
- 触发词不变：`js菜地` / `居所菜地` 等 12 条，无裸命令。

## 1.3.0

### 重构

按 EndUID 的分包约定把目录做了分类，扁平一堆 `jusuo_*.py` 改成「一个功能一个子包 + utils」：

```
HOKjusuoUID/
├── __init__.py          # 只做 Plugins 注册与子包导入
├── version.py           # 版本号唯一来源
├── jusuo_config.py      # 控制台配置
├── jusuo_residence/     # 菜地
├── jusuo_ranch/         # 牧场
├── jusuo_items/         # 物品列表
├── jusuo_market/        # 行情
├── jusuo_help/          # 帮助
├── jusuo_status/        # 状态（pm=1）
└── utils/               # api / entries / format / image / params / sender / text / view
```

- 各命令的 `SV` 与 handler 就近放在自己子包里，`utils/` 只放无状态逻辑；
- 出图发送抽到 `utils/sender.py`，菜地/牧场共用逻辑抽到 `utils/entries.py`；
- `utils/__init__.py` 保持空导入，避免 `jusuo_config ↔ utils` 循环引用；
- 发布包改为递归收集子目录（`rglob`），subpackage 会一起打进 zip。

## 1.2.0

### 变更

- 默认前缀改为 **`js`、`居所`**，`allow_empty_prefix=False`：所有命令必须带前缀（`js菜地` / `居所菜地`），不再注册裸命令；
- `居所帮助` 改名为 **`帮助`**（触发词 `js帮助` / `居所帮助`）；
- `居所状态` 改名为 **`状态`**（`js状态` / `居所状态`），仍是 `pm=1` 仅超级管理员；
- 帮助卡片与帮助文本同步为带前缀的写法。

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
