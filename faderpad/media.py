"""Media controls: now playing, play/pause, previous and next.

On Windows this uses the system media controls (the same ones behind the volume
flyout), so it works with any app that reports what it plays: Spotify, browsers,
Apple Music, VLC and so on. If those APIs aren't available it falls back to
sending the media keys, which control whatever Windows considers active.
"""
import hashlib
import os
import time

from .images import sniff_image_type

ACTIONS = ("previous", "play_pause", "next")

try:
    from winrt.windows.media.control import (
        GlobalSystemMediaTransportControlsSessionManager as SessionManager,
        GlobalSystemMediaTransportControlsSessionPlaybackStatus as PlaybackStatus,
    )
    from winrt.windows.storage.streams import DataReader

    # Not used by name, but Windows hands back types from these modules (the list of
    # sessions is a collection, playback info refers to Windows.Media). Importing them
    # here makes a missing package show up at start, and lets PyInstaller bundle them.
    import winrt.windows.foundation.collections  # noqa: F401
    import winrt.windows.media  # noqa: F401

    HAVE_WINRT = True
except Exception:  # not Windows, or the winrt packages aren't installed
    HAVE_WINRT = False

# Friendlier names for the app ids Windows reports.
KNOWN_APPS = {
    "spotify": "Spotify",
    "msedge": "Edge",
    "chrome": "Chrome",
    "firefox": "Firefox",
    "308046b0af4a39cb": "Firefox",
    "opera": "Opera",
    "brave": "Brave",
    "vlc": "VLC",
    "zunemusic": "Media Player",
    "applemusic": "Apple Music",
    "itunes": "iTunes",
    "deezer": "Deezer",
    "tidal": "TIDAL",
    "discord": "Discord",
}

MEDIA_KEYS = {"previous": 0xB1, "play_pause": 0xB3, "next": 0xB0}
COVER_RETRY = 3.0      # seconds before asking again for a cover that wasn't ready
MAX_COVER_BYTES = 5_000_000


def app_display_name(app_id):
    if not app_id:
        return ""
    low = app_id.lower()
    for key, name in KNOWN_APPS.items():
        if key in low:
            return name
    name = app_id.split("!")[-1]
    if name.lower().endswith(".exe"):
        name = name[:-4]
    return name


def send_media_key(action):
    import ctypes

    key = MEDIA_KEYS[action]
    user32 = ctypes.windll.user32
    user32.keybd_event(key, 0, 0, 0)
    user32.keybd_event(key, 0, 2, 0)  # KEYEVENTF_KEYUP


async def read_thumbnail(reference):
    """Read a cover image from Windows. Returns (bytes, mime) or (None, None)."""
    if reference is None:
        return None, None
    try:
        stream = await reference.open_read_async()
        size = int(stream.size)
        if not size or size > MAX_COVER_BYTES:
            return None, None
        reader = DataReader(stream.get_input_stream_at(0))
        await reader.load_async(size)
        data = bytearray(size)
        reader.read_bytes(data)
        data = bytes(data)
        return data, sniff_image_type(data) or getattr(stream, "content_type", None) or "image/png"
    except Exception:
        return None, None


MAX_SESSIONS = 6


class MediaController:
    def __init__(self, background):
        self._bg = background
        self._manager = None
        self._covers = {}            # cover key -> (bytes or None, mime, time)
        if HAVE_WINRT:
            self.backend = "windows"
        elif os.name == "nt":
            self.backend = "keys"
        else:
            self.backend = "none"

    # ---------- public API (called from request threads) ----------

    def state(self):
        if self.backend == "windows":
            try:
                return self._bg.run(self._windows_state(), timeout=5)
            except Exception as e:
                # Keep the buttons usable through the media keys, and say why in /api/debug.
                return self._keys_state(detail=f"{type(e).__name__}: {e}")
        if self.backend == "keys":
            return self._keys_state()
        return {"backend": "none", "available": False, "sessions": []}

    @staticmethod
    def _keys_state(detail=None):
        # We can send media keys but can't know what's playing.
        state = {"backend": "keys", "available": True, "sessions": [{
            "id": "keys", "app": "", "title": "", "artist": "", "playing": None,
            "can_previous": True, "can_next": True, "can_play_pause": True, "cover": None,
        }]}
        if detail:
            state["detail"] = detail
        return state

    def command(self, action, session_id=None):
        if action not in ACTIONS:
            raise ValueError(f"unknown action: {action!r}")
        if self.backend == "windows":
            try:
                if self._bg.run(self._windows_command(action, session_id), timeout=5):
                    return "windows"
            except Exception:
                pass
        if os.name == "nt":
            send_media_key(action)
            return "keys"
        raise RuntimeError("media controls are only available on Windows")

    def cover(self, key):
        entry = self._covers.get(key)
        if entry and entry[0]:
            return entry[0], entry[1]
        return None, None

    def debug(self):
        if self.backend != "windows":
            return {"backend": self.backend}
        state = self.state()
        result = {"backend": state.get("backend"), "sessions": state.get("sessions")}
        if state.get("detail"):
            result["detail"] = state["detail"]
        return result

    # ---------- Windows system media controls ----------

    async def _get_manager(self):
        if self._manager is None:
            self._manager = await SessionManager.request_async()
        return self._manager

    @staticmethod
    def _is_playing(session):
        try:
            return session.get_playback_info().playback_status == PlaybackStatus.PLAYING
        except Exception:
            return False

    async def _sessions(self):
        """All media sessions, each with a stable id: the app id plus a counter, because
        a browser can have several sessions (one per tab) with the same app id."""
        manager = await self._get_manager()
        result, seen = [], {}
        for session in list(manager.get_sessions() or [])[:MAX_SESSIONS]:
            app_id = session.source_app_user_model_id or "unknown"
            seen[app_id] = seen.get(app_id, 0) + 1
            result.append((f"{app_id}#{seen[app_id]}", session))
        return result

    async def _describe(self, session_id, session):
        info = session.get_playback_info()
        controls = info.controls
        props = await session.try_get_media_properties_async()
        title = (props.title or "") if props else ""
        artist = (props.artist or "") if props else ""
        app_id = session.source_app_user_model_id

        key = hashlib.sha1(f"{app_id}|{title}|{artist}".encode()).hexdigest()[:12]
        cached = self._covers.get(key)
        now = time.monotonic()
        if props and (cached is None or (cached[0] is None and now - cached[2] > COVER_RETRY)):
            data, mime = await read_thumbnail(props.thumbnail)
            self._covers[key] = (data, mime, now)
            cached = self._covers[key]

        return {
            "id": session_id,
            "app": app_display_name(app_id),
            "title": title,
            "artist": artist,
            "playing": info.playback_status == PlaybackStatus.PLAYING,
            "can_previous": bool(controls.is_previous_enabled),
            "can_next": bool(controls.is_next_enabled),
            "can_play_pause": bool(controls.is_play_pause_toggle_enabled),
            "cover": f"/api/media/cover?k={key}" if cached and cached[0] else None,
            "_cover_key": key,
        }

    async def _windows_state(self):
        sessions = []
        for session_id, session in await self._sessions():
            try:
                sessions.append(await self._describe(session_id, session))
            except Exception:
                continue  # an app closing while we read it
        # Forget covers of tracks nobody is playing any more.
        keep = {s.pop("_cover_key") for s in sessions}
        self._covers = {k: v for k, v in self._covers.items() if k in keep}
        return {"backend": "windows", "available": True, "sessions": sessions}

    async def _windows_command(self, action, session_id):
        sessions = await self._sessions()
        target = next((s for sid, s in sessions if sid == session_id), None)
        if target is None:
            # Unknown id (the app closed meanwhile): use whatever is playing, or the first one.
            target = next((s for _, s in sessions if self._is_playing(s)), None)
            if target is None and sessions:
                target = sessions[0][1]
        if target is None:
            return False
        if action == "play_pause":
            return bool(await target.try_toggle_play_pause_async())
        if action == "next":
            return bool(await target.try_skip_next_async())
        return bool(await target.try_skip_previous_async())
