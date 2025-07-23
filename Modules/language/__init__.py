from ..bootstrap import os, ctypes, locale, platform

from .en_US import en_US
from .zh_TW import zh_TW
from .zh_CN import zh_CN
from .ja_JP import ja_JP

SysPlat = platform.system()

Default = "en_US"
Words = {"en_US": en_US, "zh_TW": zh_TW, "zh_CN": zh_CN, "ja_JP": ja_JP}
Locale = {
    "950": "zh_TW",
    "936": "zh_CN",
    "932": "ja_JP",
    "1252": "en_US",
}


def translator(lang=None):

    Transl = {}

    try:
        if lang is None:
            if SysPlat == "Windows":
                buffer = ctypes.create_unicode_buffer(85)
                ctypes.windll.kernel32.GetUserDefaultLocaleName(buffer, len(buffer))
                lang = buffer.value.replace("-", "_")
            elif SysPlat in ("Linux", "Darwin"):
                lang = os.environ.get("LANG", "").split(".")[0]
            else:
                locale.setlocale(locale.LC_ALL, "")
                lang = locale.getlocale()[1].replace("cp", "")
    except Exception:
        lang = Default

    Transl = (
        Words.get(lang)
        if isinstance(lang, str) and lang in Words
        else Words.get(Locale.get(lang)) if lang in Locale else Words.get(Default)
    )

    return lambda text: Transl.get(text, text)


# 先使用自動檢測
transl = translator()
