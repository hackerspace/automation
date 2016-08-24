import time
import gc

class ManualGC:
    def __init__(self, period):
        self.period = period
        self._last = time.ticks_ms()

    def tick(self):
        if time.ticks_diff(self._last, time.ticks_ms()) > self.period:
            gc.collect()
            self._last = time.ticks_ms()
