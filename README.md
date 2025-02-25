# SlashcoSense-VRC 🎮⚡

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/)
[![OSC Protocol](https://img.shields.io/badge/OSC-1.1-brightgreen)](https://opensoundcontrol.stanford.edu/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

通过读取日志，输出Slashco VR游戏运行中的信息。

功能：

1.开局知晓地图、Slasher、生成的物品信息

2.实时刷新发电机所需的油和电数量(仅限非房主)

3.配套MA预制件，通过OSC可在游戏中查看(PC显示在屏幕,VR显示在手上)


游戏中UI默认在右上角，下面俩排格子分别代表发电机1和2，前4格白底代表缺多少油，绿色代表灌了多少油，最后一格为电池，绿色即为已安装。

[exe版本下载](https://github.com/arcxingye/SlasherSense-VRC/releases/download/exe/SlashcoSense.exe)
[配套改模包下载](https://github.com/arcxingye/SlasherSense-VRC/releases/download/exe/SlashcoSense.unitypackage)

模型参数
```
SlasherID (Int 0-13)
GENERATOR1_FUEL (Int 0-4)
GENERATOR2_FUEL (Int 0-4)
GENERATOR1_BATTERY (Bool 0-1)
GENERATOR2_BATTERY (Bool 0-1)
```
