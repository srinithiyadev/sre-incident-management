import asyncio
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import make_asgi_app
import time

from app.core.database import database, engine, metadata
from app.api import health, signals, workitems
from app.services.metrics import print_throughput

# Create all PostgreSQL tables
metadata.create_all(engine)

app = FastAPI(title="SRE Incident Management System", version="1.0.0")

# CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate limiting — max 1000 req/sec per IP
request_counts = {}

@app.middleware("http")
async def rate_limit(request: Request, call_next):
    ip    = request.client.host
    now   = time.time()
    count = request_counts.get(ip, {"count": 0, "window": now})

    if now - count["window"] > 1:
        count = {"count": 1, "window": now}
    else:
        count["count"] += 1

    request_counts[ip] = count

    if count["count"] > 1000:
        from fastapi.responses import JSONResponse
        return JSONResponse({"error": "Rate limit exceeded"}, status_code=429)

    return await call_next(request)

# Prometheus metrics endpoint
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)

# Routers
app.include_router(health.router,     tags=["Health"])
app.include_router(signals.router,    prefix="/api", tags=["Signals"])
app.include_router(workitems.router,  prefix="/api", tags=["WorkItems"])

@app.on_event("startup")
async def startup():
    await database.connect()
    # Start throughput printer in background
    asyncio.create_task(print_throughput())
    print("[IMS] Backend started successfully")

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()