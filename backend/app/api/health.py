from fastapi import APIRouter
from app.core.database import database, redis_client, mongo_db

router = APIRouter()

@router.get("/health")
async def health_check():
    status = {"status": "ok", "services": {}}

    try:
        await database.execute("SELECT 1")
        status["services"]["postgres"] = "healthy"
    except Exception as e:
        status["services"]["postgres"] = f"unhealthy: {str(e)}"
        status["status"] = "degraded"

    try:
        await redis_client.ping()
        status["services"]["redis"] = "healthy"
    except Exception as e:
        status["services"]["redis"] = f"unhealthy: {str(e)}"
        status["status"] = "degraded"

    try:
        await mongo_db.command("ping")
        status["services"]["mongo"] = "healthy"
    except Exception as e:
        status["services"]["mongo"] = f"unhealthy: {str(e)}"
        status["status"] = "degraded"

    return status
