import asyncio
import time
from prometheus_client import Counter, Gauge, REGISTRY

# Safe registration - avoid duplicate errors on restart
def get_or_register(collector, name):
    try:
        return collector
    except Exception:
        return REGISTRY._names_to_collectors[name]

try:
    signals_received  = Counter("ims_signals_total",    "Total signals received")
except ValueError:
    signals_received  = REGISTRY._names_to_collectors["ims_signals_total"]

try:
    workitems_created = Counter("ims_workitems_total",  "Total work items created")
except ValueError:
    workitems_created = REGISTRY._names_to_collectors["ims_workitems_total"]

try:
    active_incidents  = Gauge("ims_active_total",       "Currently active incidents")
except ValueError:
    active_incidents  = REGISTRY._names_to_collectors["ims_active_total"]

_signal_count_window = 0
_window_start        = time.time()

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
        print(f"[IMS METRICS] Throughput: {rate:.1f} signals/sec | Total: {int(signals_received._value.get())}")
        _signal_count_window = 0
        _window_start        = time.time()
