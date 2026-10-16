"""Bridge between Faderpad and Elgato Wave Link 3.x.

Talks to Wave Link's local WebSocket API through the wavelink-adapter library.
Nothing here is specific to one setup: channels and mixes are read from Wave Link
every time, so whatever the user has configured shows up in the web app.
"""
import asyncio
import time

from wavelink_adapter import ConnectionState, WaveLinkClient

from .images import image_data_uri

# A level meter that hasn't been updated for this long is shown as silent.
METER_TIMEOUT = 0.5


class WaveLink:
    def __init__(self, background):
        self._bg = background
        self._client = None
        self._subscribed = set()
        self._meters = {"c": {}, "m": {}}  # id -> (amplitude 0..1, time)

    # ---------- connection ----------

    async def _ensure_connected(self):
        if self._client is None:
            self._client = WaveLinkClient()
            self._client.on_typed("levelMeterChanged", self._on_meters)
        if self._client.state is not ConnectionState.CONNECTED:
            await self._client.connect()
        return self._client

    async def _fetch(self):
        client = await self._ensure_connected()
        mixes, channels = await asyncio.gather(client.get_mixes(), client.get_channels())
        targets = [("channel", c.id) for c in channels] + [("mix", m.id) for m in mixes]
        new = [t for t in targets if t not in self._subscribed]
        if new:
            self._subscribed.update(new)
            asyncio.create_task(self._subscribe_meters(client, new))
        return client, mixes, channels

    async def _subscribe_meters(self, client, targets):
        for kind, target_id in targets:
            try:
                await client.subscribe_level_meter(kind, target_id)
            except Exception:
                pass  # meters are a nice extra; the mixer works without them

    def _on_meters(self, event):
        now = time.monotonic()
        for key, entries in (("c", event.channels), ("m", event.mixes)):
            if not entries:
                continue
            # Replace the dict instead of mutating it: request threads read it concurrently.
            updated = dict(self._meters[key])
            for entry in entries:
                left = entry.level_left_percentage or 0.0
                right = entry.level_right_percentage
                updated[entry.id] = (max(left, left if right is None else right), now)
            self._meters[key] = updated

    # ---------- public API (called from request threads) ----------

    def state(self):
        return self._bg.run(self._state())

    def apply(self, change):
        return self._bg.run(self._apply(change))

    def icons(self):
        return self._bg.run(self._icons())

    def meters(self):
        now = time.monotonic()
        return {
            key: {
                target_id: (round(value, 4) if now - stamp < METER_TIMEOUT else 0)
                for target_id, (value, stamp) in self._meters[key].items()
            }
            for key in ("c", "m")
        }

    # ---------- implementation ----------

    async def _state(self):
        client, mixes, channels = await self._fetch()
        info = client.application_info
        return {
            "version": info.version if info else None,
            "mixes": [
                {"id": m.id, "name": m.name, "level": m.level, "muted": bool(m.is_muted)}
                for m in mixes
            ],
            "channels": [
                {
                    "id": c.id,
                    "name": c.name,
                    "type": c.type,
                    "level": c.level,
                    "muted": bool(c.is_muted),
                    "mixes": {
                        (cm.id or cm.mix_id): {"level": cm.level, "muted": bool(cm.is_muted)}
                        for cm in (c.mixes or [])
                    },
                }
                for c in channels
            ],
        }

    async def _apply(self, change):
        """Apply one change from the web app.

        change = {"kind": "mix", "mix": id, "level"?: 0..1, "muted"?: bool}
              or {"kind": "channel", "channel": id, "mix"?: id, "level"?: 0..1, "muted"?: bool}
        Without "mix", a channel change targets the channel's own (general) slider.
        """
        client = await self._ensure_connected()
        level = change.get("level")
        muted = change.get("muted")
        if level is not None:
            level = min(1.0, max(0.0, float(level)))
        if muted is not None:
            muted = bool(muted)

        kind = change.get("kind")
        if kind == "mix":
            mix = str(change["mix"])
            if level is not None:
                await client.set_mix_level(mix, level)
            if muted is not None:
                await client.set_mix_mute(mix, muted)
        elif kind == "channel":
            channel = str(change["channel"])
            mix = change.get("mix")
            if level is not None:
                if mix:
                    await client.set_channel_mix_level(channel, str(mix), level)
                else:
                    await client.set_channel_level(channel, level)
            if muted is not None:
                if mix:
                    await client.set_channel_mix_mute(channel, str(mix), muted)
                else:
                    await client.set_channel_mute(channel, muted)
        else:
            raise ValueError(f"unknown kind: {kind!r}")

    async def _icons(self):
        _, mixes, channels = await self._fetch()
        result = {"channels": {}, "mixes": {}}
        for key, items in (("channels", channels), ("mixes", mixes)):
            for item in items:
                uri = image_data_uri(item.image)
                if uri:
                    result[key][item.id] = uri
        return result
