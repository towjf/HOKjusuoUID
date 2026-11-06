# 居所助手 · HOKjusuoUID

> 早柚核心（gscore / gsuid_core）插件：王者荣耀世界「居所助手」数据查询 —— 菜地/牧场高倍收购、物品清单、行情走势，本地出图。

数据来自玩家自发分享的 [jusuo.playmmo.cn](https://jusuo.playmmo.cn)，插件直连其公开只读 Supabase 接口，不经网页渲染，单次查询通常在 200–400ms。

一套逻辑多平台通用：QQ、QQ 频道、微信、Telegram、KOOK、Discord、飞书等，只要 gscore 支持就能用。

## 功能

- **`js菜地` / `js牧场`**（前缀 `js` 或 `居所`，下同）：高倍收购列表，支持按物品名筛选、单价/售价两种排序、翻页；每条带商人 UID、等级、剩余时间、整批预计售价。
- **`js物品列表`**：列出两类当前在售的全部物品名（纯文本）。
- **`js行情`**：近 N 小时各物品的最高成交估价峰值。
- **本地出图**：Pillow 绘制 960px 宽卡片，深蓝配色 + 大字号，不联网、约 0.2 秒一张；绘制失败自动退纯文本。
- **AI 可调用**：命令注册时带 `to_ai` 描述，接入了 AI Core 的环境可直接用自然语言触发。

## 效果

| 菜地 · 售价优先 | 菜地 · 单价优先 |
| --- | --- |
| ![菜地售价](docs/images/residence-sale.webp) | ![菜地单价](docs/images/residence-unit.webp) |

| 牧场 · 售价优先 | 行情 · 近 24 小时 |
| --- | --- |
| ![牧场](docs/images/ranch-sale.webp) | ![行情](docs/images/market.webp) |

## 安装

插件目录名、`Plugins(name=...)` 都必须叫 **HOKjusuoUID**，三者（仓库名 / 目录名 / 注册名）保持一致，gscore 才能正确加载。

**方式一：网页控制台（推荐）**

打开 gscore 控制台 → 插件管理 → 安装插件 → 填仓库地址 `https://github.com/towjf/HOKjusuoUID`，安装完成后启用。

**方式二：git clone**

```bash
cd gsuid_core/plugins
git clone https://github.com/towjf/HOKjusuoUID.git
```

**方式三：上传 zip**

仓库的 `dist/` 里有两个包，按安装器行为二选一：

| 包 | 结构 | 用在哪 |
| --- | --- | --- |
| `HOKjusuoUID-flat.zip` | 根层直接是 `__init__.py`、`utils/`、`jusuo_*/` | 控制台「上传 zip 安装」时用；安装器会自己建 `plugins/HOKjusuoUID/` |
| `HOKjusuoUID.zip` | 根层是 `HOKjusuoUID/` 文件夹 | 手动解压到 `gsuid_core/plugins/` 后直接用 |

手动解压时最终目录必须是：

```
gsuid_core/plugins/HOKjusuoUID/
├── __init__.py          # 仅 Plugins 注册 + 导入子包
├── version.py           # 版本号（唯一来源）
├── jusuo_config.py      # 网页控制台配置项
├── jusuo_residence/     # 菜地命令
├── jusuo_ranch/         # 牧场命令
├── jusuo_items/         # 物品列表命令
├── jusuo_market/        # 行情命令
├── jusuo_help/          # 帮助命令
├── jusuo_status/        # 状态命令（pm=1）
└── utils/
    ├── api.py           # Supabase REST 客户端（httpx，缓存 + 重试）
    ├── entries.py       # 菜地/牧场共用取数
    ├── params.py        # 参数解析（纯函数）
    ├── view.py          # 数据 → 卡片视图模型
    ├── image.py         # Pillow 绘制（改配色/字号只动这里）
    ├── sender.py        # 出图并发送（失败退纯文本）
    ├── text.py          # 纯文本兜底
    └── format.py        # 金额、时间、估价公式

```bash
# 单元测试（不需要 gscore，有 Pillow 即可）
python -m unittest discover -s tests -p "test_*.py"

# 冒烟测试：用桩模块假装 gscore，真实拉数据跑全部命令
python tests/smoke_test.py
```

`tests/stub_gsuid_core/` 是给冒烟测试用的最小桩，不会被 gscore 加载。

## 更新日志

见 [CHANGELOG.md](CHANGELOG.md)。

## 免责声明

本插件为非官方工具，与游戏官方、`jusuo.playmmo.cn` 站点均无隶属关系；数据版权归原站点与分享玩家所有。请合理控制请求频率，因数据偏差造成的游戏内损失由使用者自行承担。

## License

[MIT](LICENSE)
