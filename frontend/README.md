# SRE Incident Management System

Built by Srinithiya M for the Zeotap Infrastructure / SRE Intern Assignment.

---

## What This System Does

In a production environment, hundreds of services emit error signals every second.
Without a system to manage these signals, engineers get overwhelmed.

This IMS solves that by:
- Ingesting high-volume signals without crashing
- Grouping related signals into one incident (debouncing)
- Guiding engineers through a structured resolution workflow
- Enforcing Root Cause Analysis before closing any incident
- Providing real-time visibility via Grafana dashboards

---

## Architecture

┌─────────────────────────────────────────────┐
                │           SIGNAL PRODUCERS                   │
                │  (APIs, RDBMS, Cache, MQ, NoSQL, MCP Hosts) │
                └──────────────────┬──────────────────────────┘
                                   │ HTTP POST /api/signals
                                   ▼
                ┌─────────────────────────────────────────────┐
                │         FASTAPI BACKEND (Async)              │
                │                                              │
                │  ┌─────────────┐    ┌──────────────────┐   │
                │  │ Rate Limiter│    │  Debounce Engine  │   │
                │  │ 1000 req/s  │───▶│  10s window       │   │
                │  └─────────────┘    └────────┬─────────┘   │
                │                              │               │
                │              ┌───────────────┼────────────┐ │
                │              ▼               ▼            ▼ │
                │        ┌──────────┐  ┌──────────┐  ┌───────┐│
                │        │ MongoDB  │  │PostgreSQL│  │ Redis ││
                │        │(Raw Log) │  │(WorkItems│  │(Cache)││
                │        └──────────┘  │   + RCA) │  └───────┘│
                │                      └──────────┘           │
                │  ┌──────────────────────────────────────┐   │
                │  │         Prometheus /metrics           │   │
                │  └──────────────────────────────────────┘   │
                └─────────────────────────────────────────────┘
                                   │
                ┌──────────────────┼──────────────────────────┐
                │                  │                           │
                ▼                  ▼                           ▼
         ┌──────────┐      ┌──────────────┐          ┌──────────────┐
         │  React   │      │  Prometheus  │          │   Grafana    │
         │Dashboard │      │  (Metrics)   │─────────▶│ (Dashboard)  │
         └──────────┘      └──────────────┘          └──────────────┘

---

## Tech Stack & Why

| Component | Technology | Why I Chose It |
|---|---|---|
| Backend | FastAPI (Python) | Native async support handles 10k signals/sec without blocking |
| Signal Queue | Redis Streams | Production-capable buffer — prevents backend crash during DB slowness |
| Raw Signal Store | MongoDB | Schema-free — every signal payload shape is different |
| Work Items + RCA | PostgreSQL | ACID transactions ensure state changes are atomic |
| Hot Cache | Redis | Sub-millisecond reads for live dashboard — no DB query on every refresh |
| Metrics | Prometheus + Grafana | Industry standard — leveraged from my prior SRE project experience |
| Frontend | React | Component-based UI with auto-refresh every 5 seconds |
| Packaging | Docker Compose | One-command setup for all 6 services |

### Production Upgrade Path

| Current | At Scale |
|---|---|
| Redis Streams | Apache Kafka (millions/sec) |
| Single PostgreSQL | Patroni HA Cluster |
| Docker Compose | Kubernetes + HPA |

---

## How I Handled Backpressure

Backpressure is what happens when signals arrive faster than the persistence layer can handle.

### The Problem
If 10,000 signals/sec arrive and MongoDB can only write 1,000/sec the system crashes.

### My Solution — Three Layers

**Layer 1 — Rate Limiter (First Defense)**

Ingestion API has a rate limiter of 1000 requests/sec per IP.
If exceeded the API returns HTTP 429 Too Many Requests immediately.

**Layer 2 — Async Processing (Second Defense)**

FastAPI processes each signal asynchronously using async/await.
One slow DB write never blocks other signals from being processed.

**Layer 3 — Debouncing (Third Defense)**

100 signals for CACHE_CLUSTER_01 in 10 seconds creates only 1 WorkItem in PostgreSQL.
All 100 signals are stored in MongoDB.
This reduces PostgreSQL write load by up to 99%.

---

## Design Patterns Used

### 1. State Pattern — Incident Lifecycle

Manages valid transitions only:

OPEN → INVESTIGATING → RESOLVED → CLOSED

Invalid transitions are rejected with a clear error message.
CLOSED state requires a complete RCA — enforced automatically.

### 2. Strategy Pattern — Priority Assignment

Different component types get different priorities automatically:

- RDBMS → P0 (most critical)
- API → P1 (high)
- MQ → P1 (high)
- CACHE → P2 (medium)

New component types can be added without changing core logic.

### 3. Debounce Pattern — Signal Deduplication

Signal arrives → Check component_id in memory window.
If seen within 10 seconds → Skip WorkItem creation, increment counter.
If new or expired → Create WorkItem, reset window.

---

## Quick Start

```bash
git clone https://github.com/srinithiyadev/sre-incident-management.git
cd sre-incident-management
docker-compose up --build
```

Wait 2 minutes for all services to initialize.

### Access Points

| Service | URL |
|---|---|
| Frontend Dashboard | http://localhost:3000 |
| Backend API | http://localhost:8000 |
| API Documentation | http://localhost:8000/docs |
| Health Check | http://localhost:8000/health |
| Prometheus | http://localhost:9090 |
| Grafana | http://localhost:3001 (admin/admin) |

---

## Simulate a Failure

```bash
cd sample_data
python3 mock_failure.py
```

This simulates:
1. RDBMS outage — 20 signals → 1 P0 incident
2. MCP Host failure — 15 signals → 1 P1 incident
3. Cache degradation — 10 signals → 1 P2 incident
4. Queue overflow — 10 signals → 1 P1 incident

---

## Incident Workflow

1. Signal arrives → Debounce → WorkItem created as OPEN
2. Engineer sees alert on dashboard
3. Moves to INVESTIGATING and starts working
4. Applies fix and moves to RESOLVED
5. Fills RCA form (mandatory)
6. System calculates MTTR automatically
7. Moves to CLOSED

If engineer tries to CLOSE without RCA the system returns:
Cannot close incident without RCA. Submit RCA first.

---

## Unit Tests

```bash
cd backend
python3 -m pytest tests/test_rca.py -v
```

12 tests covering:
- All valid state transitions
- All invalid state transitions
- RCA field validation
- MTTR calculation accuracy

---

## Non-Functional Features

| Feature | Implementation | Benefit |
|---|---|---|
| Rate Limiting | 1000 req/sec per IP | Prevents cascade failures |
| Health Check | /health endpoint | Monitors all 3 databases |
| Throughput Metrics | Console every 5 sec | Real-time visibility |
| Prometheus Metrics | /metrics endpoint | Grafana integration |
| CORS | Configured middleware | Secure frontend access |
| Input Validation | Pydantic models | Prevents bad data |
| Auto Restart | Docker restart policy | Self-healing services |

---

## Screenshots

### Live Incident Dashboard
![Incident List](docs/screenshots/incident-list.png)

### Incident Detail with Raw Signals
![Incident Detail](docs/screenshots/incident-detail.png)

### RCA Form
![RCA Form](docs/screenshots/rca-form.png)

### Grafana Metrics Dashboard
![Grafana](docs/screenshots/grafana-dashboard.png)

### Health Check
![Health](docs/screenshots/health-check.png)

### API Documentation
![Swagger](docs/screenshots/swagger-docs.png)

### Mock Failure Simulation
![Mock](docs/screenshots/mock-simulation.png)

### Unit Tests — 12/12 Passing
![Tests](docs/screenshots/unit-tests.png)

---

## Project Structure

```text
sre-incident-management/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── models/
│   │   ├── services/
│   │   └── core/
│   ├── tests/
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── src/
│   └── Dockerfile
├── prometheus/
├── sample_data/
├── docs/
├── docker-compose.yml
└── README.md
```
---

## Author

**Srinithiya M**

GitHub: https://github.com/srinithiyadev/sre-incident-management

Assignment: Zeotap Infrastructure / SRE Intern 2026