import os
import sys
from pathlib import Path

from PyInstaller.utils.hooks import collect_submodules


ROOT = Path(SPECPATH).resolve().parent
VERSION = os.environ.get("TRADE_TRANSLATOR_VERSION", "0.1.1")
IS_WINDOWS = sys.platform == "win32"
IS_MACOS = sys.platform == "darwin"
CONSOLE = os.environ.get("TRADE_TRANSLATOR_CONSOLE") == "1"

icon_path = ROOT / "icons" / (
    "app.ico" if IS_WINDOWS else "app.icns"
)
version_path = (
    ROOT / "packaging" / "windows_version_info.txt"
    if IS_WINDOWS
    else None
)

a = Analysis(
    [str(ROOT / "app" / "main.py")],
    pathex=[str(ROOT)],
    binaries=[],
    datas=[],
    hiddenimports=collect_submodules("keyring.backends"),
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=["PyQt5", "PyQt6"],
    noarchive=False,
    optimize=0,
)

# Qt 6.10 uses the ICU library provided by Windows. Development tools can expose
# an unrelated private ICU build on PATH; bundling it makes Qt6Core fail to load
# with WinError 127.
if IS_WINDOWS:
    excluded_windows_icu = {"icuuc.dll", "icudt78.dll"}
    a.binaries = [
        binary
        for binary in a.binaries
        if Path(binary[0]).name.lower() not in excluded_windows_icu
    ]

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="TradeTranslator",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=CONSOLE,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=str(icon_path),
    version=str(version_path) if version_path else None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    name="TradeTranslator",
)

if IS_MACOS:
    app = BUNDLE(
        coll,
        name="Trade Translator.app",
        icon=str(icon_path),
        bundle_identifier="app.trade-translator.desktop",
        version=VERSION,
        info_plist={
            "CFBundleDisplayName": "Trade Translator",
            "CFBundleShortVersionString": VERSION,
            "CFBundleVersion": VERSION,
            "LSMinimumSystemVersion": "13.0",
            "NSAppleScriptEnabled": False,
            "NSHighResolutionCapable": True,
            "NSPrincipalClass": "NSApplication",
        },
    )
