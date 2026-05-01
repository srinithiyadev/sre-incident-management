import asyncio
from datetime import datetime
from typing import Dict

# In-memory debounce window tracker
# component_id -> first_seen timestamp
_debounce_window: Dict[str, datetime] = {}
_debounce_lock = asyncio.Lock()

DEBOUNCE_SECONDS = 10

async def should_create_workitem(component_id: str) -> bool:
    """
    Returns True if a new WorkItem should be created.
    Returns False if this component is already in debounce window.
    """
    async with _debounce_lock:
        now = datetime.utcnow()
        last_seen = _debounce_window.get(component_id)

        if last_seen is None:
            _debounce_window[component_id] = now
            return True

        elapsed = (now - last_seen).total_seconds()
        if elapsed > DEBOUNCE_SECONDS:
            _debounce_window[component_id] = now
            return True

        return False