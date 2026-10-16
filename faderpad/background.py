"""A single asyncio event loop running in a background thread.

Flask handles each request in its own thread, while the Wave Link client and the
Windows media APIs are asynchronous. Everything async runs on this one loop and
request threads wait for the result with ``run()``.
"""
import asyncio
import threading


class Background:
    def __init__(self):
        self.loop = asyncio.new_event_loop()
        self._thread = threading.Thread(target=self._run, name="faderpad-async", daemon=True)
        self._thread.start()

    def _run(self):
        asyncio.set_event_loop(self.loop)
        try:
            # Windows media controls use WinRT, which needs a COM apartment on this thread.
            from winrt.runtime import MTA, init_apartment
            init_apartment(MTA)
        except Exception:
            pass  # not on Windows, winrt missing, or already initialised
        self.loop.run_forever()

    def run(self, coro, timeout=10):
        """Run a coroutine on the background loop and wait for its result."""
        return asyncio.run_coroutine_threadsafe(coro, self.loop).result(timeout)
