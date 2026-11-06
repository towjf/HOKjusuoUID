"""冒烟测试：用 tests/stub 里的 gsuid_core 桩跑真实数据，验证插件集成面。

用法（仓库根目录）：
    python tests/smoke_test.py
"""

import asyncio
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STUB = Path(__file__).resolve().parent / "stub"

sys.path.insert(0, str(STUB))  # 提供 gsuid_core 桩
sys.path.insert(0, str(ROOT))  # 提供 HOKjusuoUID 包

import HOKjusuoUID  # noqa: E402
from gsuid_core.models import Event  # noqa: E402
from gsuid_core.sv import HANDLERS, PLUGIN_KWARGS, SV_LIST  # noqa: E402

from HOKjusuoUID.jusuo_config import jusuo_config  # noqa: E402


class FakeBot:
    """记录 bot.send 的内容。"""

    def __init__(self):
        self.sends = []

    async def send(self, message):
        self.sends.append(message)
        return message


CASES = [
    ("菜地", " 草莓 单价 2"),
    ("牧场", " 羊毛"),
    ("物品列表", ""),
    ("行情", " 牧场 48"),
    ("居所帮助", ""),
    ("居所状态", ""),
]


async def main() -> None:
    print(f"插件：{HOKjusuoUID.__name__} v{HOKjusuoUID.__version__}")
    print("Plugins 参数：", PLUGIN_KWARGS.get("HOKjusuoUID"))
    print()
    print("SV 列表（每个命令一个，可单独开关/设权限）：")
    for name, sv in SV_LIST.items():
        keys = [k for k, v in HANDLERS.items() if v["sv"] == name]
        print(f"  {name:18} pm={sv.pm}  触发词={keys}")
    print()
    duplicates = {
        key: sum(1 for k in HANDLERS if k == key) for key in set(HANDLERS)
    }
    extra = [k for k, c in duplicates.items() if c > 1]
    print("重复注册的命令：", extra or "无")
    print("全部触发词：", sorted(HANDLERS))
    print("配置项：", list(jusuo_config.config.keys()))
    print()

    for command, text in CASES:
        handler = HANDLERS[command]["func"]
        bot = FakeBot()
        await handler(bot, Event(text=text, raw_text=command + text, command=command))
        sent = bot.sends[0] if bot.sends else None
        if isinstance(sent, str) and sent.startswith("base64://"):
            desc = f"图片（base64 {len(sent) // 1024}KB）"
        elif isinstance(sent, str):
            desc = "文本：" + sent.splitlines()[0][:36]
        else:
            desc = str(type(sent))
        print(f"{command:6}+{text!r:12} -> {desc}  [sv={HANDLERS[command]['sv']}]")

    jusuo_config.get_config("use_image").data = False
    bot = FakeBot()
    await HANDLERS["菜地"]["func"](bot, Event(text="", command="菜地"))
    print("\n关闭出图后的纯文本输出（前两行）：")
    for line in str(bot.sends[0]).splitlines()[:2]:
        print("   ", line)

    from HOKjusuoUID.jusuo_params import parse_entries_args, tokens

    print()
    for raw in ["", "草莓", "草莓 单价 2", "倍率2 等级70 售价"]:
        print(f"解析 {raw!r} ->", parse_entries_args(tokens(raw)))


if __name__ == "__main__":
    asyncio.run(main())
