# -*- mode: python ; coding: utf-8 -*-

excludes = [
    'unittest', 'test', 'doctest', 'pydoc', 'pydoc_data',
    'pdb', 'bdb', 'cProfile', 'profile', 'pstats', 'tracemalloc',
    'distutils', '_distutils_hack', 'setuptools', 'pip', 'venv',
    'lib2to3', 'idlelib', 'turtledemo', 'turtle', 'tkinter',
    '__pycache__',
    'numpy', 'pandas', 'scipy', 'matplotlib',
    'pytest', '_pytest', 'nose', 'mock',
    'requests', 'flask', 'jinja2', 'sqlalchemy',
    'PIL', 'Pillow', 'pygame',
    'curses', 'ftplib', 'gdbm', 'mailbox', 'nntplib', 
    'poplib', 'smtpd', 'smtplib', 'telnetlib', 'webbrowser',
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