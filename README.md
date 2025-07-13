# SlashcoSense-VRC 🎮⚡

[![Python 3.13+](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/)
[![OSC Protocol](https://img.shields.io/badge/OSC-1.1-brightgreen)](https://opensoundcontrol.stanford.edu/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

透過讀取日誌，輸出 Slashco VR 遊戲執行中的資訊。更新後可能會失效。

### UI 預覽:
![](https://github.com/user-attachments/assets/28d5bb26-caec-4399-9293-3f336076ad99)

### 功能：

1.開局知曉地圖、Slasher、生成的物品資訊

2.即時刷新發電機所需的油和電數量(僅限非房主)

3.配套MA預製件，透過 OSC 可在遊戲中檢視

4.PCVR雙適配，PC顯示在螢幕，VR顯示在左手上，均可調節

5.多語言支援 (繁中|簡中|英文|日文)，AI翻譯


### 預製件的安裝方法 (**原作者編譯，非本項目**)：
MA安裝，無需調整，直接放進模型裡就行，不要放在子集裡。

[exe版本下載](https://github.com/arcxingye/SlasherSense-VRC/releases/download/exe/SlashcoSense.exe)
[MA預製件下載](https://github.com/arcxingye/SlasherSense-VRC/releases/download/exe/SlashcoSense.unitypackage)

OSC 傳送參數
```
SlasherID (Int 0-13)
GENERATOR1_FUEL (Int 0-4)
GENERATOR2_FUEL (Int 0-4)
GENERATOR1_BATTERY (Bool 0-1)
GENERATOR2_BATTERY (Bool 0-1)
```
