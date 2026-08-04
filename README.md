# Task API with SQLite Database

A lightweight RESTful CRUD API for managing to-do tasks, built with Python, FastAPI, Pydantic, and SQLite for permanent data persistence.

## Database Overview

This API uses **SQLite** (`tasks.db`) for storing tasks persistently on disk across server restarts.

### Why SQLite?
- **Zero Configuration:** No external database server (like PostgreSQL or MySQL) is required to install or manage.
- **Single File Persistence:** The entire database lives in a local file (`tasks.db`), making it portable and easy to inspect.
- **Built into Python:** Uses Python's standard `sqlite3` module without external database drivers.

### Schema Design (`tasks` table)

| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | `INTEGER` | `PRIMARY KEY AUTOINCREMENT` | Unique auto-incrementing identifier |
| `title` | `TEXT` | `NOT NULL` | Description of the task |
| `done` | `BOOLEAN` | `NOT NULL DEFAULT 0` | Completion status (`0` = false, `1` = true) |

### Example SQL Queries

```sql
-- Read all tasks
SELECT * FROM tasks;

-- Read all completed tasks
SELECT * FROM tasks WHERE done = 1;

-- Insert a new task
INSERT INTO tasks (title, done) VALUES ('Learn SQLite', 0);

-- Update task status
UPDATE tasks SET done = 1 WHERE id = 4;

-- Delete a task
DELETE FROM tasks WHERE id = 4;
```

---

## Database Viewer

Tasks table inspected via the SQLite Viewer:

![Database Viewer](database.png)

---

## How to run it

1. **Clone this repo**
   ```bash
   git clone https://github.com/hafsat-abdulhamid/crud-api.git
   cd crud-api
   ```

2. **Create virtual environment**
   ```bash
   python3 -m venv .venv
   ```

3. **Activate virtual environment**
   ```bash
   source .venv/bin/activate
   ```

4. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

5. **Start the server**
   ```bash
   uvicorn main:app --reload
   ```
   The API will be running at `http://localhost:8000`.

---

## Endpoints

| Method | Path | Description | Status codes |
|---|---|---|---|
| `GET` | `/` | API info | `200` |
| `GET` | `/health` | Health check | `200` |
| `GET` | `/tasks` | List all tasks from SQLite (with search/filter/sort) | `200` |
| `GET` | `/tasks/{id}` | Get one task by ID from SQLite | `200`, `404` |
| `GET` | `/stats` | Task statistics (total, completed, pending) | `200` |
| `POST` | `/tasks` | Create a task in SQLite | `201`, `400` |
| `PUT` | `/tasks/{id}` | Update a task in SQLite | `200`, `400`, `404` |
| `DELETE` | `/tasks/{id}` | Delete a task from SQLite | `204`, `404` |

---

## Example curl output

```bash
$ curl -i -X POST http://localhost:8000/tasks -H "Content-Type: application/json" -d '{"title":"Add task to SQLite"}'

HTTP/1.1 201 Created
date: Tue, 04 Aug 2026 06:29:44 GMT
server: uvicorn
content-length: 49
content-type: application/json

{"id":4,"title":"Add task to SQLite","done":false}
```

---

## Swagger UI

Interactive OpenAPI documentation is available at `http://localhost:8000/docs` while the server is running:

![Swagger UI](swagger.png)

---

## AI vs Me (Stage 6: The AI Rematch)

In Stage 6, a full migration prompt was written to instruct an AI assistant to migrate the in-memory CRUD API to SQLite in quarantine (`ai-version/main.py`), and the resulting code was compared against the hand-crafted implementation.

### The Migration Prompt

```markdown
You are a senior Python backend engineer.

I have an existing FastAPI CRUD application that currently stores tasks in memory. Your job is to migrate the application to SQLite while preserving the API behavior.

## Requirements

### Tech Stack
* Python
* FastAPI
* SQLite using Python's built-in `sqlite3` module
* Do not use SQLAlchemy or any ORM.

### Database
Create a SQLite database containing a table named `tasks`.
The table should have the following schema:
* `id` INTEGER PRIMARY KEY AUTOINCREMENT
* `title` TEXT NOT NULL
* `done` BOOLEAN DEFAULT 0

When the application starts:
* Create the `tasks` table if it does not already exist.
* Seed the database with exactly three default tasks only if the table is empty.
* Do not reseed every time the application restarts.

### API Behavior
Keep the existing endpoint behavior exactly the same.
- GET /tasks: Return all tasks.
- GET /tasks/{id}: Return the requested task (404 if not found).
- POST /tasks: Create a new task (201 Created, 400 on empty/whitespace title).
- PUT /tasks/{id}: Update task title and completion status (404 if not found, 400 on empty/whitespace title).
- DELETE /tasks/{id}: Delete the task (204 No Content, 404 if not found).

### Database Access
* Use parameterized SQL queries (`?`) for every query that accepts user input.
* Do not build SQL statements using string concatenation or f-strings.
```

### Concrete Differences Found (Diff Review)

1. **Batch Seeding with `executemany` (AI did better):**
   The AI version used `cursor.executemany("INSERT INTO tasks VALUES (?, ?)", [...])` to insert all 3 seed tasks in a single database transaction rather than 3 consecutive `cursor.execute()` calls.

2. **Automatic Trimming on Write (AI design choice):**
   The AI automatically sanitized user input by calling `.strip()` before inserting or updating strings (`task.title.strip()`), ensuring trailing whitespace is never persisted.

3. **Missing Query Features & Stats Endpoint (Hand-built was more feature-rich):**
   Because the prompt focused only on core CRUD, the AI did not include the SQL `LIKE` search, status filtering, alphabetical sorting, or the `GET /stats` summary endpoint that our hand-built API provides.
