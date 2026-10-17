"""First-run choices: whether Faderpad starts with Windows.

The choice is kept in %APPDATA%\Faderpad\settings.json (not in faderpad.json, which is for
settings the user writes by hand). Starting with Windows is one value in the current user's
"Run" registry key: no administrator rights needed, and removing it undoes everything.
"""
import json
import os
import sys
from pathlib import Path

try:
    import winreg
except ImportError:  # not Windows
    winreg = None

RUN_KEY = r"Software\Microsoft\Windows\CurrentVersion\Run"
RUN_NAME = "Faderpad"


def supported():
    """Only the packaged .exe can start with Windows: there is a fixed file to point at."""
    return winreg is not None and bool(getattr(sys, "frozen", False))


def _settings_path():
    return Path(os.environ.get("APPDATA", Path.home())) / "Faderpad" / "settings.json"


def _read():
    try:
        with open(_settings_path(), encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, dict) else {}
    except (OSError, ValueError):
        return {}


def is_done():
    """True once the user has seen the welcome screen."""
    return bool(_read().get("setup_done"))


def autostart_enabled():
    if not supported():
        return False
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, RUN_KEY) as key:
            winreg.QueryValueEx(key, RUN_NAME)
        return True
    except OSError:
        return False


def set_autostart(enabled):
    if not supported():
        raise OSError("starting with Windows needs the packaged Faderpad.exe")
    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, RUN_KEY, 0, winreg.KEY_SET_VALUE) as key:
        if enabled:
            winreg.SetValueEx(key, RUN_NAME, 0, winreg.REG_SZ, f'"{sys.executable}"')
        else:
            try:
                winreg.DeleteValue(key, RUN_NAME)
            except FileNotFoundError:
                pass


def mark_done():
    path = _settings_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    data = _read()
    data["setup_done"] = True
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f)


def refresh_autostart():
    """If the .exe was moved, point the startup entry at its new place."""
    if autostart_enabled():
        try:
            set_autostart(True)
        except OSError:
            pass
