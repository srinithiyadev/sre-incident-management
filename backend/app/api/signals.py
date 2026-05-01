from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from datetime import datetime
import uuid

from app.core.database import database, mongo_db, redis_client
from app.services.debounce import should_create_workitem
from app.services.metrics import record_signal, workitems_created, active_incidents
from app.models.workitem import workitems

router = APIRouter()

PRIORITY_MAP = {
    "RDBMS":        "P0",
    "API":          "P1",
    "MQ":           "P1",
    "CACHE":        "P2",
    "NOSQL":        "P2",
    "DISTRIBUTED":  "P3",
}

class SignalPayload(BaseModel):
    component_id:   str
    component_type: str
    error_message:  str
    severity:       str = "ERROR"

@router.post("/signals")
async def ingest_signal(payload: SignalPayload):
    record_signal()

    # Store raw signal in MongoDB
    signal_doc = {
        "signal_id":      str(uuid.uuid4()),
        "component_id":   payload.component_id,
        "component_type": payload.component_type,
        "error_message":  payload.error_message,
        "severity":       payload.severity,
        "timestamp":      datetime.utcnow().isoformat(),
    }
    await mongo_db.signals.insert_one(signal_doc)

    # Debounce — only create WorkItem if not already in window
    create_new = await should_create_workitem(payload.component_id)

    workitem_id = None
    if create_new:
        priority    = PRIORITY_MAP.get(payload.component_type.upper(), "P3")
        workitem_id = str(uuid.uuid4())
        now         = datetime.utcnow()

        await database.execute(
            workitems.insert().values(
                id           = workitem_id,
                component_id = payload.component_id,
                title        = f"[{priority}] Incident: {payload.component_id}",
                status       = "OPEN",
                priority     = priority,
                signal_count = 1,
                start_time   = now,
                created_at   = now,
            )
        )

        # Cache in Redis for fast dashboard reads
        await redis_client.hset(f"workitem:{workitem_id}", mapping={
            "id":           workitem_id,
            "component_id": payload.component_id,
            "status":       "OPEN",
            "priority":     priority,
            "created_at":   now.isoformat(),
        })

        workitems_created.inc()
        active_incidents.inc()
    else:
        # Increment signal count on existing workitem
        await database.execute(
            workitems.update()
            .where(workitems.c.component_id == payload.component_id)
            .values(signal_count=workitems.c.signal_count + 1)
        )

    return {"accepted": True, "workitem_created": create_new, "workitem_id": workitem_id}