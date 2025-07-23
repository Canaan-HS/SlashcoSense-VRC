from ...bootstrap import re
from ...language import Transl

ITEMS = {
    "Proxy-Locator": Transl("定位器"),
    "Royal Burger": Transl("皇家漢堡"),
    "Cookie": Transl("餅乾"),
    "Beer Keg": Transl("啤酒桶"),
    "Mayonnaise": Transl("美乃滋"),
    "Orange Jello": Transl("橙色果凍"),
    "Costco Frozen Pizza": Transl("COSTCO速凍披薩"),
    "Airport Jungle Juice": Transl("機場的烈性酒"),
    "Rhino Pill": Transl("犀牛丸"),
    "The Rock": Transl("岩石"),
    "LabMeat": Transl("人造肉"),
    "Lab-Grown Meat": Transl("人造肉"),
    "Pocket Sand": Transl("沙袋"),
    "The Baby": Transl("巫毒娃娃"),
    "Newport Menthols": Transl("紐波特薄荷"),
    "B-GONE Soda": Transl("B-GONE蘇打水"),
    "Red40": Transl("40號紅色染劑"),
    "Red40 Vial": Transl("40號紅色染劑"),
    "Milk Jug": Transl("桶裝牛奶"),
    "Pot of Greed": Transl("貪婪之壺"),
    "Deathward": Transl("不死圖騰"),
    "Evil Jonkler Cart": Transl("邪惡的瓊克爾•卡特"),
    "25 Gram Benadryl": Transl("25克苯海拉明"),
    "Balkan Boost": Transl("巴爾幹激素"),
}

# 編譯物品解析正則
ITEMS_PATTERN = re.compile(
    "|".join(re.escape(key) for key in sorted(ITEMS.keys(), key=len, reverse=True)), re.IGNORECASE
)


def ParseItems(items: str) -> str:
    """解析物品列表"""
    if not items:
        return ""

    matches = list(ITEMS_PATTERN.finditer(items))
    if not matches:
        return items

    result = []
    last_end = 0

    for match in matches:
        start, end = match.span()

        if start > last_end:
            unmatched = items[last_end:start].strip()
            if unmatched:
                result.append(unmatched)

        result.append(ITEMS[match.group()])
        last_end = end

    if last_end < len(items):
        unmatched = items[last_end:].strip()
        if unmatched:
            result.append(unmatched)

    return " / ".join(result)
