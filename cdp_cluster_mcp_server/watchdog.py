import threading
import time
from .config import settings

class WatchdogRuntime:
    def __init__(self):
        self._stop = False
        self._thread = None
        self.last_tick = None
        self.last_result = None

    def start(self, tick_fn):
        if self._thread and self._thread.is_alive():
            return
        self._stop = False
        self._thread = threading.Thread(target=self._loop, args=(tick_fn,), daemon=True)
        self._thread.start()

    def stop(self):
        self._stop = True

    def _loop(self, tick_fn):
        while not self._stop:
            try:
                self.last_result = tick_fn()
                self.last_tick = time.time()
            except Exception as e:
                self.last_result = {"status": "error", "message": str(e)}
                self.last_tick = time.time()
            time.sleep(settings.watchdog_interval_seconds)

runtime = WatchdogRuntime()
