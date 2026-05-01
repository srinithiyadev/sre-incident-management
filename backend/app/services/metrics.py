import asyncio
import time

# Simple counters without prometheus to avoid registry conflicts
_signals_total   = 0
_workitems_total = 0
_active_total    = 0

_signal_count_window = 0
_window_start        = time.time()

class SimpleCounter:
    def __init__(self): self._value = 0
    def inc(self): self._value += 1
    def get(self): return self._value

class SimpleGauge:
    def __init__(self): self._value = 0
    def inc(self): self._value += 1
    def dec(self): self._value -= 1
    def get(self): return self._value

signals_received  = SimpleCounter()
workitems_created = SimpleCounter()
active_incidents  = SimpleGauge()

def record_signal():
    global _signal_count_window
    signals_received.inc()
    _signal_count_window += 1

async def print_throughput():
    global _signal_count_window, _window_start
    while True:
        await asyncio.sleep(5)
        elapsed = time.time() - _window_start
        rate    = _signal_count_window / elapsed if elapsed > 0 else 0
        print(f"[IMS METRICS] Throughput: {rate:.1f} signals/sec | Total: {signals_received.get()}")
        _signal_count_window = 0
        _window_start        = time.time()
