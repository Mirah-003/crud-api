# Task API — Containerized PostgreSQL Stack (A3)

A production-grade RESTful Task Management API built with **FastAPI**, **PostgreSQL**, and **Docker Compose**.

## Features
- **Full CRUD Endpoints**: `GET /tasks`, `GET /tasks/{id}`, `POST /tasks`, `PUT /tasks/{id}`, `DELETE /tasks/{id}`
- **PostgreSQL Persistence**: Data persists across container restarts using Docker Volume (`taskdata`)
- **Zero-Config Setup**: `.env.example` template with git-ignored `.env` secret management
- **Docker Compose Orchestration**: Single command bring-up with database healthcheck dependency ordering

---

## Quick Start (One Command)

1. Clone repository & enter directory:
   ```bash
   git clone https://github.com/Mirah-003/crud-api.git
   cd crud-api
   ```

2. Create environment configuration:
   ```bash
   cp .env.example .env
   ```

3. Launch the full stack:
   ```bash
   docker compose up --build
   ```

4. API is available at `http://localhost:8000`
   - Interactive OpenAPI Docs: `http://localhost:8000/docs`

5. Stop stack:
   ```bash
   docker compose down
   ```

---

## API Endpoints Table

| Method | Endpoint | Description | Expected Status |
|---|---|---|---|
| `GET` | `/` | API Root & Metadata | `200 OK` |
| `GET` | `/health` | Application Health Check | `200 OK` |
| `GET` | `/stats` | Task Aggregation Statistics | `200 OK` |
| `GET` | `/tasks` | List Tasks (supports `search`, `done`, `sort`) | `200 OK` |
| `GET` | `/tasks/{id}` | Get Single Task by ID | `200 OK` / `404 Not Found` |
| `POST` | `/tasks` | Create New Task | `201 Created` / `400 Bad Request` |
| `PUT` | `/tasks/{id}` | Update Task Title/Done State | `200 OK` / `404 Not Found` |
| `DELETE` | `/tasks/{id}` | Delete Task | `204 No Content` / `404 Not Found` |

---

## Sample `curl -i` Verification Output

```http
HTTP/1.1 201 Created
date: Sat, 15 Aug 2026 09:15:00 GMT
server: uvicorn
content-length: 53
content-type: application/json

{"id":4,"title":"Test persistence task","done":false}
```

---

## Database Verification

![Database Verification](db-screenshot.png)

---

## Architectural Insight: Why Storage is Just an Implementation Detail

Across Assignments A1, A2, and A3, our FastAPI core application logic and external API HTTP contracts (`/tasks`) remained virtually unchanged:
1. **A1**: In-memory Python lists
2. **A2**: SQLite local file database (`tasks.db`)
3. **A3**: PostgreSQL relational database engine running in Docker

Because our HTTP route definitions and response schemas stayed consistent, client applications consuming this API did not require a single line of code change when we swapped from SQLite to containerized PostgreSQL. This demonstrates that **storage is merely an implementation detail behind an interface boundary**.

---

## AI vs Me (Stage 6 Comparison)
- **AI Approach**: Defaulted to single-stage container build without explicit container healthchecks, leading to database connection race conditions upon container boot.
- **Human Senior Engineer Refinement**: Implemented explicit `healthcheck` (`pg_isready`) in `docker-compose.yml` with `depends_on.condition: service_healthy`, ensuring strict startup order and zero runtime connection failures.