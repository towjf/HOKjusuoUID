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
├── __init__.py          ← 必须在这一层（只做 Plugins 注册 + 导入子包）
├── version.py
├── jusuo_config.py
├── jusuo_residence/     # 菜地
│   └── __init__.py
├── jusuo_ranch/         # 牧场
│   └── __init__.py
├── jusuo_items/         # 物品列表
│   └── __init__.py
├── jusuo_market/        # 行情
│   └── __init__.py
├── jusuo_help/          # 帮助
│   └── __init__.py
├── jusuo_status/        # 状态（仅超管）
│   └── __init__.py
└── utils/
    ├── __init__.py
    ├── api.py           # Supabase REST 客户端
    ├── entries.py       # 菜地/牧场共用取数
    ├── format.py        # 金额、时间、估价公式
    ├── image.py         # Pillow 绘制
    ├── params.py        # 参数解析
    ├── sender.py        # 出图并发送
    ├── text.py          # 纯文本兜底
    └── view.py          # 卡片视图模型
```

**别套两层**（`plugins/HOKjusuoUID/HOKjusuoUID/__init__.py` 这种会加载失败，表现就是日志里看不到 `插件HOKjusuoUID导入成功!`）。

重启 gscore，日志出现 `插件HOKjusuoUID导入成功!` 即成功。依赖只有 `httpx` 与 `Pillow`，gscore 自带。

## 命令

**所有命令都必须带前缀 `js` 或 `居所`**，裸命令不注册（避免和其他插件撞名）。下文用 `js` 举例，换成 `居所` 完全等价。

| 命令 | 说明 |
| --- | --- |
| `js菜地 [物品] [单价\|售价] [页数]` | 菜地作物高倍收购，默认售价优先、第 1 页 |
| `js牧场 [物品] [单价\|售价] [页数]` | 牧场动物产物收购，规则同上 |
| `js物品列表` | 菜地 + 牧场在售物品名清单 |
| `js行情 [菜地\|牧场] [小时]` | 行情峰值，默认菜地、24 小时 |
| `js帮助` | 命令一览（图片） |
| `js状态` | 自检：接口连通性、出图方式、版本（**仅超级管理员**） |

示例：

```
js菜地                     → 全部物品，售价优先第 1 页
居所菜地 草莓               → 只看名字含「草莓」的
js菜地 草莓 单价 2          → 草莓类，按单价排序第 2 页
js牧场 羊毛                → 只看羊毛类产物
居所行情 牧场 48            → 牧场产物近 48 小时峰值
js物品列表                 → 列出两类全部物品名
```

附加过滤（可选，默认不过滤）：`js菜地 倍率2 等级70 售价`。

## 前缀与权限

前缀走**插件级配置的「强制前缀」**，与 EndUID（`end` / `zmd`）、GenshinUID 等插件一致：

```python
Plugins(
    name="HOKjusuoUID",
    prefix=[],                      # 默认前缀：关闭
    force_prefix=["js", "居所"],     # 强制前缀：js、居所
    allow_empty_prefix=False,      # 允许空前缀：关闭 → 没有裸命令
)
```

对应控制台「插件服务配置」里的三行：

| 配置项 | 值 |
| --- | --- |
| 默认前缀（`prefix`） | 关闭 / 空 |
| 强制前缀（`force_prefix`） | `js`、`居所` |
| 允许空前缀（`allow_empty_prefix`） | 关 |

强制前缀由插件作者固定、不写入 `data/plugins_config/HOKjusuoUID.json`，部署者不会误删；`allow_empty_prefix=False` 保证 `菜地` 这类裸命令不会触发，所有指令都必须带 `js` 或 `居所`。

每条命令是一个独立 SV，可以单独开关、单独设权限与优先级：

| SV | 触发词 | 默认权限 |
| --- | --- | --- |
| HOKjusuoUID-菜地 | `js菜地` / `居所菜地` | 6 所有人 |
| HOKjusuoUID-牧场 | `js牧场` / `居所牧场` | 6 所有人 |
| HOKjusuoUID-物品列表 | `js物品列表` / `居所物品列表` | 6 所有人 |
| HOKjusuoUID-行情 | `js行情` / `居所行情` | 6 所有人 |
| HOKjusuoUID-帮助 | `js帮助` / `居所帮助` | 6 所有人 |
| HOKjusuoUID-自检 | `js状态` / `居所状态` | **1 超级管理员** |

权限等级：0 主人 / 1 超级管理员 / 2 群主 / 3 群管理员 / 6 普通用户。

> SV 里每个命令出现「两条触发器」（`jsX`、`居所X`）是正常的：gscore 会按前缀列表展开，两条分别是两个前缀，不是重复注册。

## 配置

配置会写入 `gsuid_core/data/HOKjusuoUID/config.json`，也可在网页控制台修改。

| 键 | 说明 | 默认 |
| --- | --- | --- |
| `supabase_url` | 数据接口地址 | `https://db.playmmo.cn` |
| `anon_key` | 公开只读 key，留空用内置 | 空 |
| `timeout` | 请求超时（秒） | `15` |
| `cache_ttl` | 基础数据缓存秒数 | `90` |
| `default_sort` | 默认排序：`售价` / `单价` | `售价` |
| `page_size` | 每页条数 | `10` |
| `hide_limited` | 排除已限购条目 | `true` |
| `fetch_limit` | 单次拉取条数 | `300` |
| `use_image` | 输出图片卡片 | `true` |
| `market_hours` | 行情默认小时数 | `24` |

## 数据与隐私

- 数据全部来自 `db.playmmo.cn` 的公开只读接口（站点前端内置的 anon key，仅有 RLS 允许的读权限），插件不写入、不上传任何数据；
- 卡片在本地绘制，图片不经过任何第三方渲染服务；
- 展示的商人 UID 等信息是站点本身公开的玩家分享内容，仅供游戏内找摊位使用；
- 估价按站点公式推算：`单价 ×(1+等级加成)× 倍率 × 数量 ×(1+满贡献0.2)`，与游戏内实际成交可能存在差异。

> 站点接口由第三方维护，若对方调整字段或鉴权，插件需要同步更新。欢迎提 issue。

## 开发

```
HOKjusuoUID/
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
```

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
