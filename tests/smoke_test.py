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
sys.path.insert(0, str(ROOT))  # 提供 gs_jusuo 包

import gs_jusuo  # noqa: E402
from gsuid_core.models import Event  # noqa: E402
from gsuid_core.sv import HANDLERS, PLUGIN_KWARGS  # noqa: E402

from gs_jusuo.jusuo_config import jusuo_config  # noqa: E402


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
    print(f"插件：{gs_jusuo.__name__} v{gs_jusuo.__version__}")
    print("Plugins 参数：", PLUGIN_KWARGS.get("gs_jusuo"))
    print("已注册命令：", sorted(HANDLERS))
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
        print(f"{command:6}+{text!r:12} -> {desc}")

    jusuo_config.get_config("use_image").data = False
    bot = FakeBot()
    await HANDLERS["菜地"]["func"](bot, Event(text="", command="菜地"))
    print("\n关闭出图后的纯文本输出（前两行）：")
    for line in str(bot.sends[0]).splitlines()[:2]:
        print("   ", line)

    # 顺手验证参数解析的边界
    from gs_jusuo.jusuo_params import parse_entries_args, tokens

    for raw in ["", "草莓", "草莓 单价 2", "倍率2 等级70 售价"]:
        print(f"解析 {raw!r} ->", parse_entries_args(tokens(raw)))


if __name__ == "__main__":
    asyncio.run(main())
