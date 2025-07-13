# -*- mode: python ; coding: utf-8 -*-

excludes = [
    # 客製化 GUI / TUI (若您的專案未使用)
    # 使用 PySide6/PyQt5，就不需要 Tkinter。
    'tkinter', 'turtle', 'turtledemo', 'curses',
    'winsound', 'colorsys', 'chunk', 'imghdr',
    'sndhdr', 'ossaudiodev',

    # 測試與偵錯 (Testing & Debugging)
    # 這些是開發時才用到的工具，發布時完全不需要。
    'unittest', 'test', 'doctest', 'pytest', '_pytest',
    'nose', 'mock', 'tox', 'hypothesis', 'pdb', 
    'bdb', 'cProfile', 'profile', 'pstats', 'tracemalloc', 
    'pydoc', 'tests', 'pydoc_data', 'lib2to3', 'pickletools'

    # 開發與外帶工具 (Development & Packaging Tools)
    # 應用程式執行時不需要外帶工具本身。
    'distutils', '_distutils_hack', 'setuptools', 'pip', 'venv',
    'zipapp', 'lib2to3', 'pyclbr', 'pydoc', 'pydoc_data',
    'idlelib', 'pkg_resources', 'ensurepip', 'wheel'

    # PyInstaller 相關工具和包
    'altgraph', 'pyinstaller_hooks_contrib', '_pyinstaller_hooks_contrib',
    'pefile', 'packaging', 'pywin32_system32',

    # Windows 特定組件 (激進)
    'win32com', 'win32ctypes', 'win32api', 'win32con',
    'pywintypes', 'win32cred', 'win32file', 'win32pipe', 'win32process'

    # 網絡與 Web 服務
    'email', 'ftplib', 'telnetlib', 'nntplib',
    'poplib', 'smtpd', 'smtplib', 'mailbox', 'asyncio',
    'ssl', '_ssl', 'http', 'urllib.request', 'gopherlib',
    'imaplib', 'wsgiref', 'webbrowser', 'cgi', 'cgitb',
    'xmlrpc'

    # 科學與網頁框架 (若未使用)
    'numpy', 'pandas', 'scipy', 'matplotlib',
    'requests', 'flask', 'jinja2', 'werkzeug', 'sqlalchemy',
    'PIL', 'Pillow', 'pygame',

    # 數據庫
    'sqlite3', 'dbm', 'gdbm', 'dbm.gnu', 'dbm.ndbm', 'dbm.dumb',

    # 數據解析
    # 排除除 JSON 和基本配置外的所有數據格式處理器
    'xml', 'xml.dom', 'xml.sax', 'xml.etree', 'csv', 'configparser',
    'html', 'email', 'json.tool', 'tarfile', 'zipapp', 'plistlib', 'xdrlib',

    # 加密與壓縮
    'hmac', 'secrets', 'bz2', 'lzma', 'gzip', 'zlib', 

    # 並發與多進程
    'multiprocessing', 'concurrent',

    # 不常用標準庫
    'getopt', 'calendar', 'optparse', 'getpass',
    'decimal', 'fractions', 'statistics',
    'msilib', 'shelve', 'symtable', 'tabnanny'

    # 以下為有風險 (激進) 排除
    'msvcrt', 'pickle', 'hashlib', '_hashlib',

    # 古老 / 少用語系
    'encodings.koi8_r', 'encodings.koi8_t', 'encodings.koi8_u', 'encodings.kz1048',
    'encodings.mac_cyrillic', 'encodings.mac_greek', 'encodings.mac_iceland',
    'encodings.mac_latin2', 'encodings.mac_roman', 'encodings.mac_turkish',
    'encodings.iso8859_2', 'encodings.iso8859_3', 'encodings.iso8859_4',
    'encodings.iso8859_5', 'encodings.iso8859_6', 'encodings.iso8859_7',
    'encodings.iso8859_8', 'encodings.iso8859_10', 'encodings.iso8859_11',
    'encodings.iso8859_13', 'encodings.iso8859_14',
    'encodings.iso8859_15', 'encodings.iso8859_16',
    'encodings.cp037', 'encodings.cp273', 'encodings.cp424',
    'encodings.cp500', 'encodings.cp720', 'encodings.cp737', 'encodings.cp775',
    'encodings.cp850', 'encodings.cp855', 'encodings.cp858', 'encodings.cp861',
    'encodings.cp862', 'encodings.cp863', 'encodings.cp864',
    'encodings.cp865', 'encodings.cp866', 'encodings.cp869', 'encodings.cp874',
    'encodings.cp875', 'encodings.cp1006', 'encodings.cp1026',
    'encodings.cp1125', 'encodings.cp1140', 'encodings.palmos',
    'encodings.ptcp154', 'encodings.tis_620', 'encodings.hp_roman8',

    # 單位區域不必要的
    'encodings.cp1250', 'encodings.cp1251', 'encodings.cp1253',
    'encodings.cp1254', 'encodings.cp1255', 'encodings.cp1256',
    'encodings.cp1257', 'encodings.cp1258',
    'encodings.iso8859_5', 'encodings.iso8859_6',
    #'encodings.iso8859_7', 'encodings.iso8859_9',

    # DOS 特定語系
    'encodings.cp852', 'encodings.cp860',
]

# 排除二進制包
excluded_packages = [
    'PyInstaller', '_pyinstaller_hooks_contrib', 'pyinstaller_hooks_contrib',
    'pip', 'setuptools', 'pkg_resources', 'altgraph', 'win32ctypes', 'packaging', 'pefile'
]

# 排除不需要的文件類型
excluded_file_types = ['.pdb', '.lib', '.a', '.ilk', '.exp', '.map']

a = Analysis(
    ['../SlashcoSense.pyw'],
    pathex=[],
    binaries=[],
    datas=[('../IMG/SlashCo.ico', '.')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=excludes,
    noarchive=False,
    optimize=2,
)

a.binaries = [
    binary for binary in a.binaries
    if not any(binary[0].startswith(prefix) for prefix in excluded_packages)
    and not any(binary[1].lower().endswith(ext) for ext in excluded_file_types)
]

pyz = PYZ(a.pure, a.zipped_data, compress=True)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='SlashcoSense',
    debug=False,
    icon='../IMG/SlashCo.ico',
    strip=True,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
)