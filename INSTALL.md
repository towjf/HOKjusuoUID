# 安装说明（HOKjusuoUID）

gscore 认插件的唯一依据是**目录名**：`gsuid_core/plugins/HOKjusuoUID/` 里必须直接躺着 `__init__.py`。
仓库名、目录名、`Plugins(name="HOKjusuoUID")` 三者一致才能加载。

## 正确形态（对照检查）

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

## 三个包怎么用

| 包 | 根层内容 | 放到哪 |
| --- | --- | --- |
| `HOKjusuoUID.zip` | `HOKjusuoUID/` 文件夹 | 解压到 `gsuid_core/plugins/` → 解压完直接可用 |
| `HOKjusuoUID-flat.zip` | `__init__.py`、`jusuo_*.py` | 先建目录 `plugins/HOKjusuoUID/`，**解压到这个目录里面** |

Windows 资源管理器右键「解压到当前文件夹」和「解压到 HOKjusuoUID\」很容易搞错，推荐直接用命令行：

```powershell
# 任选一种，路径按你的实际环境改
$plugins = "C:\gsuid_core\gsuid_core\plugins"

# ① 用 folder 包：解压到 plugins/ 下
Expand-Archive -Path .\HOKjusuoUID.zip -DestinationPath $plugins -Force

# ② 用 flat 包：先建目录再解压进去
$dst = Join-Path $plugins "HOKjusuoUID"
New-Item -ItemType Directory -Force $dst | Out-Null
Expand-Archive -Path .\HOKjusuoUID-flat.zip -DestinationPath $dst -Force
```

```bash
# Linux / Docker
unzip HOKjusuoUID.zip -d /gsuid_core/gsuid_core/plugins
# 或
mkdir -p /gsuid_core/gsuid_core/plugins/HOKjusuoUID
unzip HOKjusuoUID-flat.zip -d /gsuid_core/gsuid_core/plugins/HOKjusuoUID
```

## 装完自检

```powershell
Test-Path "$plugins\HOKjusuoUID\__init__.py"   # 必须返回 True
```

重启 gscore，日志里应出现：

```
插件HOKjusuoUID导入成功!
```

看不到这行就是层级不对，按下面修。

## 常见错误形态 → 修法

**① 多套了一层**（最常见，`__init__.py` 在插件目录的下一层）

```
plugins/HOKjusuoUID/HOKjusuoUID/__init__.py   ✗
```

```powershell
$dst = "$plugins\HOKjusuoUID"
Move-Item "$dst\HOKjusuoUID\*" $dst -Force
Remove-Item "$dst\HOKjusuoUID" -Recurse -Force
```

**② 文件直接散在 plugins/ 根目录**

```
plugins/__init__.py                            ✗
```

```powershell
$dst = "$plugins\HOKjusuoUID"
New-Item -ItemType Directory -Force $dst | Out-Null
Move-Item "$plugins\__init__.py" "$plugins\jusuo_*.py" $dst -Force
```

**③ 目录名不对**（比如还是 `gs_jusuo`、`HOKjusuoUID-main`）

```powershell
Rename-Item "$plugins\gs_jusuo" "HOKjusuoUID"
```

## 推荐：直接 git clone

绕开所有解压层级问题：

```bash
cd gsuid_core/plugins
git clone https://github.com/towjf/HOKjusuoUID.git
```

`git clone` 出来的目录天生就是 `plugins/HOKjusuoUID/__init__.py`，结构一定正确；以后更新直接 `git pull`。
