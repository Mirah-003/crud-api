# Task API with SQLite

This is a task management API I built using Python, FastAPI, and SQLite. It started as an in-memory CRUD app from Assignment 1, and in this assignment I swapped the storage to a real SQLite database so that tasks actually persist between server restarts.

I had used SQLite before but never really understood it deeply. Building this project stage by stage helped me finally see how the pieces connect — from writing raw SQL to seeing the results show up in the SQLite Viewer.

## My Process

I worked through this assignment in stages, committing after each one:

1. **Stage 0** — Set up the database connection and wrote the `init_db()` function to create the table and seed it with starter tasks. Getting the structure right (what goes where in the file, what syntax to use) was honestly the trickiest part early on.
2. **Stage 1** — Replaced the in-memory `GET` endpoints with `SELECT` queries.
3. **Stage 2** — Replaced the `POST` endpoint with an `INSERT` query. The moment I stopped the server, restarted it, and saw my data still there was when it really clicked.
4. **Stage 3** — Replaced `PUT` and `DELETE` with `UPDATE` and `DELETE FROM` queries.
5. **Stage 4** — Explored the database visually using the SQLite Viewer extension in VS Code.
6. **Stage 5** — Documented everything in this README.
7. **Bonus** — Added search, filtering by status, sorting, and a `/stats` endpoint that uses `COUNT(*)` directly in SQL.
8. **Stage 6** — Wrote a migration prompt, generated an AI version in quarantine (`ai-version/`), and compared the two implementations side by side.

My approach was: read the documentation first, then watch tutorials to see how things come together visually, then work through pseudocode and translate it into actual code. When I hit errors, I would read the error message carefully, figure out what it means, and take note of it so I don't repeat the same mistake. The moment things really clicked was when I put my pseudocode and my actual code side by side and could clearly see what each line was doing instead of just following instructions.

## What I Learned

- The API endpoints don't change at all when you swap from memory to a database. Persistence is an implementation detail behind the same interface.
- SQLite is literally just a file (`tasks.db`) sitting in my project folder. No server to install, no configuration.
- Parameterized queries (`?`) exist to prevent SQL injection. You never glue user input directly into a SQL string.
- `conn.commit()` is crucial — without it, your changes don't actually save to disk.
- `conn.row_factory = sqlite3.Row` lets you access columns by name (like `row["title"]`) instead of by index number.

---

## Database

The API stores tasks in a SQLite database file called `tasks.db`.

### Table schema

| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | `INTEGER` | `PRIMARY KEY AUTOINCREMENT` | Auto-incrementing unique ID |
| `title` | `TEXT` | `NOT NULL` | Task description |
| `done` | `BOOLEAN` | `NOT NULL DEFAULT 0` | 0 = not done, 1 = done |

### SQL queries used in this project

```sql
SELECT * FROM tasks;
SELECT * FROM tasks WHERE id = ?;
SELECT * FROM tasks WHERE done = 1;
SELECT * FROM tasks WHERE title LIKE '%search%';
INSERT INTO tasks (title, done) VALUES (?, ?);
UPDATE tasks SET title = ?, done = ? WHERE id = ?;
DELETE FROM tasks WHERE id = ?;
SELECT COUNT(*) FROM tasks;
```

### Database Viewer

Here is the tasks table viewed through the SQLite Viewer VS Code extension:

![Database Viewer](database.png)

---

## How to run it

1. Clone this repo
   ```bash
   git clone https://github.com/hafsat-abdulhamid/crud-api.git
   cd crud-api
   ```

2. Create and activate virtual environment
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. Install dependencies
   ```bash
   pip install -r requirements.txt
   ```

4. Start the server
   ```bash
   uvicorn main:app --reload
   ```
   The API runs at `http://localhost:8000`. The database file (`tasks.db`) is created automatically on first startup.

---

## Endpoints

| Method | Path | Description | Status codes |
|---|---|---|---|
| `GET` | `/` | API info | `200` |
| `GET` | `/health` | Health check | `200` |
| `GET` | `/tasks` | List tasks (supports `?search=`, `?done=`, `?sort=title`) | `200` |
| `GET` | `/tasks/{id}` | Get one task | `200`, `404` |
| `GET` | `/stats` | Task counts (total, completed, pending) | `200` |
| `POST` | `/tasks` | Create a task | `201`, `400` |
| `PUT` | `/tasks/{id}` | Update a task | `200`, `400`, `404` |
| `DELETE` | `/tasks/{id}` | Delete a task | `204`, `404` |

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

Interactive docs at `http://localhost:8000/docs`:

![Swagger UI](swagger.png)

---

## AI vs Me (Stage 6)

For Stage 6, I wrote a detailed prompt specifying the migration requirements and had an AI generate its own version in `ai-version/main.py`. My hand-built code stays untouched — the AI version is quarantined in its own folder.

### The prompt I wrote

```markdown
You are a senior Python backend engineer.

I have an existing FastAPI CRUD application that currently stores tasks in memory.
Your job is to migrate the application to SQLite while preserving the API behavior.

Requirements:
- Python, FastAPI, SQLite (built-in sqlite3 module, no ORM)
- Table: tasks (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT NOT NULL, done BOOLEAN DEFAULT 0)
- On startup: create table if missing, seed 3 default tasks only if table is empty
- Endpoints: GET /tasks, GET /tasks/{id}, POST /tasks (201), PUT /tasks/{id}, DELETE /tasks/{id} (204)
- 404 when task not found, 400 on empty/whitespace title
- Use parameterized queries (?) everywhere, no string concatenation for SQL
```

### Three things I noticed when comparing

1. **The AI used `executemany` for seeding** — it batched all 3 inserts into one call instead of 3 separate `cursor.execute()` lines. That's more efficient but I didn't know about `executemany` when I wrote mine.

2. **The AI stripped whitespace before saving** — it called `.strip()` on the title before inserting/updating, so trailing spaces never get stored. My version validates but doesn't trim before saving.

3. **The AI didn't include any extras** — no search, no filtering, no sorting, no `/stats`. It only built what the prompt asked for, which makes sense. My version has more features because I built those as bonus tasks.
