from base64 import b64encode


async def convert_img(img, is_base64=False):
    """桩：返回 base64:// 字符串。"""
    if isinstance(img, bytes):
        data = img
    else:
        data = bytes(img)
    return "base64://" + b64encode(data).decode()
