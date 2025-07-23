from ...bootstrap import re
from ...language import transl

ITEMS = {
    "Proxy-Locator": transl("定位器"),
    "Royal Burger": transl("皇家漢堡"),
    "Cookie": transl("餅乾"),
    "Beer Keg": transl("啤酒桶"),
    "Mayonnaise": transl("美乃滋"),
    "Orange Jello": transl("橙色果凍"),
    "Costco Frozen Pizza": transl("COSTCO速凍披薩"),
    "Airport Jungle Juice": transl("機場的烈性酒"),
    "Rhino Pill": transl("犀牛丸"),
    "The Rock": transl("岩石"),
    "LabMeat": transl("人造肉"),
    "Lab-Grown Meat": transl("人造肉"),
    "Pocket Sand": transl("沙袋"),
    "The Baby": transl("巫毒娃娃"),
    "Newport Menthols": transl("紐波特薄荷"),
    "B-GONE Soda": transl("B-GONE蘇打水"),
    "Red40": transl("40號紅色染劑"),
    "Red40 Vial": transl("40號紅色染劑"),
    "Milk Jug": transl("桶裝牛奶"),
    "Pot of Greed": transl("貪婪之壺"),
    "Deathward": transl("不死圖騰"),
    "Evil Jonkler Cart": transl("邪惡的瓊克爾•卡特"),
    "25 Gram Benadryl": transl("25克苯海拉明"),
    "Balkan Boost": transl("巴爾幹激素"),
}

# 編譯物品解析正則
ITEMS_PATTERN = re.compile(
    "|".join(re.escape(key) for key in sorted(ITEMS.keys(), key=len, reverse=True)), re.IGNORECASE
)


def parse_items(items: str) -> str:
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
