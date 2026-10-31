"""Event logging."""

import json
from datetime import datetime, timezone
from pathlib import Path


def emit_event(events_log: Path, event_name: str, data: dict):
    """Emit JSONL event."""
    event = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "event": event_name,
        **data,
    }
    
    with open(events_log, 'a') as f:
        f.write(json.dumps(event, ensure_ascii=False))
        f.write('\n')
        f.flush()
