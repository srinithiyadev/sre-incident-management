from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from datetime import datetime
from typing import Optional
import uuid

from app.core.database import database, mongo_db, redis_client
from app.models.workitem import workitems, rca_records
from app.services.state_machine import WorkItemStateMachine, InvalidTransitionError
from app.services.metrics import active_incidents

router = APIRouter()

class StatusUpdate(BaseModel):
    new_status: str

class RCAPayload(BaseModel):
    root_cause:       str
    category:         str
    fix_applied:      str
    prevention_steps: str
    incident_start:   datetime
    incident_end:     datetime

@router.get("/workitems")
async def list_workitems():
    rows = await database.fetch_all(
        workitems.select().order_by(workitems.c.created_at.desc())
    )
    return [dict(r) for r in rows]

@router.get("/workitems/{workitem_id}")
async def get_workitem(workitem_id: str):
    row = await database.fetch_one(
        workitems.select().where(workitems.c.id == workitem_id)
    )
    if not row:
        raise HTTPException(status_code=404, detail="WorkItem not found")

    signals = await mongo_db.signals.find(
        {"component_id": row["component_id"]},
        {"_id": 0}
    ).to_list(100)

    return {"workitem": dict(row), "signals": signals}

@router.patch("/workitems/{workitem_id}/status")
async def update_status(workitem_id: str, body: StatusUpdate):
    row = await database.fetch_one(
        workitems.select().where(workitems.c.id == workitem_id)
    )
    if not row:
        raise HTTPException(status_code=404, detail="WorkItem not found")

    # Block CLOSED if no RCA
    if body.new_status == "CLOSED":
        rca = await database.fetch_one(
            rca_records.select().where(rca_records.c.workitem_id == workitem_id)
        )
        if not rca:
            raise HTTPException(
                status_code=400,
                detail="Cannot close incident without RCA. Submit RCA first."
            )

    # State machine validation
    try:
        sm = WorkItemStateMachine(row["status"])
        sm.transition(body.new_status)
    except InvalidTransitionError as e:
        raise HTTPException(status_code=400, detail=str(e))

    await database.execute(
        workitems.update()
        .where(workitems.c.id == workitem_id)
        .values(status=body.new_status)
    )

    # Update Redis cache
    await redis_client.hset(f"workitem:{workitem_id}", "status", body.new_status)

    if body.new_status == "CLOSED":
        active_incidents.dec()

    return {"updated": True, "new_status": body.new_status}

@router.post("/workitems/{workitem_id}/rca")
async def submit_rca(workitem_id: str, payload: RCAPayload):
    row = await database.fetch_one(
        workitems.select().where(workitems.c.id == workitem_id)
    )
    if not row:
        raise HTTPException(status_code=404, detail="WorkItem not found")

    # MTTR calculation
    mttr = (payload.incident_end - payload.incident_start).total_seconds() / 60

    await database.execute(
        rca_records.insert().values(
            id               = str(uuid.uuid4()),
            workitem_id      = workitem_id,
            root_cause       = payload.root_cause,
            category         = payload.category,
            fix_applied      = payload.fix_applied,
            prevention_steps = payload.prevention_steps,
            incident_start   = payload.incident_start,
            incident_end     = payload.incident_end,
            submitted_at     = datetime.utcnow(),
        )
    )

    # Update MTTR on workitem
    await database.execute(
        workitems.update()
        .where(workitems.c.id == workitem_id)
        .values(mttr_minutes=mttr, end_time=payload.incident_end)
    )

    return {"rca_submitted": True, "mttr_minutes": round(mttr, 2)}