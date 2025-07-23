import os
import re
import sys
import locale
import ctypes
import platform

from pathlib import Path
from datetime import datetime
from typing import Optional, Any, TYPE_CHECKING

from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QTextEdit,
    QCheckBox,
    QLineEdit,
    QGroupBox,
)
from PySide6.QtCore import Qt, QUrl, QSize, QTimer, Signal, QThread, QObject
from PySide6.QtGui import QFont, QIcon, QCursor, QPixmap, QPainter, QPixmapCache, QPainterPath
from PySide6.QtNetwork import QNetworkAccessManager, QNetworkRequest, QNetworkReply

# 避免可能出現的錯誤, 事先初始化一些全域變數
udp_client = None
SimpleUDPClient = None
UDP_CLIENT_AVAILABLE = False

try:
    from pythonosc import udp_client
    UDP_CLIENT_AVAILABLE = True
except ImportError:
    pass

if TYPE_CHECKING:
    from pythonosc.udp_client import SimpleUDPClient
