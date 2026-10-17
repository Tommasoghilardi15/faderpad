# PyInstaller recipe for Faderpad.exe
# Build with:  pyinstaller --noconfirm --clean faderpad.spec
from PyInstaller.utils.hooks import collect_all

datas = [("faderpad/web", "faderpad/web")]
binaries = []
hiddenimports = [
    "winrt.runtime",
    "winrt.windows.foundation",
    "winrt.windows.foundation.collections",
    "winrt.windows.media",
    "winrt.windows.media.control",
    "winrt.windows.storage.streams",
    "webview.platforms.edgechromium",
]

# The winrt packages ship compiled modules; collect them all so media controls work in the .exe.
try:
    winrt_datas, winrt_binaries, winrt_hidden = collect_all("winrt")
    datas += winrt_datas
    binaries += winrt_binaries
    hiddenimports += winrt_hidden
except Exception:
    pass

a = Analysis(
    ["run_faderpad.py"],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    excludes=["tkinter"],
)
pyz = PYZ(a.pure)
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="Faderpad",
    icon="assets/icon.ico",
    console=False,
    upx=False,
)
