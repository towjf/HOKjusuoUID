"""消息发送：出图优先，失败退纯文本。"""

from __future__ import annotations

from gsuid_core.bot import Bot
from gsuid_core.logger import logger
from gsuid_core.utils.image.convert import convert_img

from ..jusuo_config import conf
from .image import render_card
from .text import card_to_text


async def send_card(bot: Bot, card: dict) -> None:
    """把卡片视图模型发出去：Pillow 出图 → base64；异常则发纯文本。"""
    if not conf("use_image"):
        await bot.send(card_to_text(card))
        return
    try:
        png = render_card(card)
        await bot.send(await convert_img(png))
    except Exception as exc:  # noqa: BLE001
        logger.exception(f"[HOKjusuoUID] 出图失败，改用纯文本: {exc}")
        await bot.send(card_to_text(card))
