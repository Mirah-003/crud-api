import os
from typing import Optional
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import psycopg2
from psycopg2.extras import RealDictCursor

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

class TaskCreate(BaseModel):
    title: str

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    done: Optional[bool] = None

app = FastAPI(title="Task API (AI Version)")

def get_db_connection():
    conn = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id SERIAL PRIMARY KEY,
            title TEXT NOT NULL,
            done BOOLEAN NOT NULL DEFAULT FALSE
        )
    """)
    cursor.execute("SELECT COUNT(*) AS count FROM tasks")
    count = cursor.fetchone()["count"]
    if count == 0:
        cursor.executemany(
            "INSERT INTO tasks (title, done) VALUES (%s, %s)",
            [
                ("Complete stage 0 and commit to git", True),
                ("Complete stage 1 and commit to git", True),
                ("Complete stage 2 and commit to git", False),
            ]
        )
    conn.commit()
    cursor.close()
    conn.close()

init_db()

@app.get("/", summary="Root endpoint")
def read_root():
    return {
        "name": "Task API (AI Version)",
        "version": "1.0",
        "endpoints": ["/tasks"]
    }

@app.get("/health", summary="Health check")
def health():
    return {"status": "ok"}

@app.get("/tasks", summary="List all tasks")
def get_tasks(search: Optional[str] = None, done: Optional[bool] = None, sort: Optional[str] = None):
    conn = get_db_connection()
    cursor = conn.cursor()

    query = "SELECT * FROM tasks"
    conditions = []
    params = []

    if search:
        conditions.append("title LIKE %s")
        params.append(f"%{search}%")

    if done is not None:
        conditions.append("done = %s")
        params.append(done)

    if conditions:
        query += " WHERE " + " AND ".join(conditions)

    if sort == "title":
        query += " ORDER BY title ASC"
    else:
        query += " ORDER BY id ASC"

    cursor.execute(query, tuple(params))
    rows = cursor.fetchall()
    cursor.close()
    conn.close()

    return [{"id": row["id"], "title": row["title"], "done": bool(row["done"])} for row in rows]

@app.get("/stats", summary="Get task statistics")
def get_stats():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) AS total FROM tasks")
    total = cursor.fetchone()["total"]
    cursor.execute("SELECT COUNT(*) AS completed FROM tasks WHERE done = TRUE")
    completed = cursor.fetchone()["completed"]
    cursor.execute("SELECT COUNT(*) AS pending FROM tasks WHERE done = FALSE")
    pending = cursor.fetchone()["pending"]
    cursor.close()
    conn.close()
    return {"total_tasks": total, "completed_tasks": completed, "pending_tasks": pending}

@app.get("/tasks/{task_id}", summary="Get a single task")
def get_task(task_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tasks WHERE id = %s", (task_id,))
    row = cursor.fetchone()
    cursor.close()
    conn.close()

    if row is None:
        raise HTTPException(status_code=404, detail="Task not found")

    return {"id": row["id"], "title": row["title"], "done": bool(row["done"])}

@app.post("/tasks", status_code=201, summary="Create a new task")
def create_task(task: TaskCreate):
    if not task.title.strip():
        raise HTTPException(status_code=400, detail="Title cannot be empty")

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO tasks (title, done) VALUES (%s, %s) RETURNING *",
        (task.title.strip(), False)
    )
    new_task = cursor.fetchone()
    conn.commit()
    cursor.close()
    conn.close()

    return {"id": new_task["id"], "title": new_task["title"], "done": bool(new_task["done"])}

@app.put("/tasks/{task_id}", summary="Update a task")
def update_task(task_id: int, task: TaskUpdate):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tasks WHERE id = %s", (task_id,))
    existing = cursor.fetchone()

    if existing is None:
        cursor.close()
        conn.close()
        raise HTTPException(status_code=404, detail="Task not found")

    new_title = existing["title"] if task.title is None else task.title.strip()
    new_done = existing["done"] if task.done is None else task.done

    if task.title is not None and not task.title.strip():
        cursor.close()
        conn.close()
        raise HTTPException(status_code=400, detail="Title cannot be empty")

    cursor.execute(
        "UPDATE tasks SET title = %s, done = %s WHERE id = %s",
        (new_title, new_done, task_id)
    )
    conn.commit()
    cursor.close()
    conn.close()

    return {"id": task_id, "title": new_title, "done": bool(new_done)}

@app.delete("/tasks/{task_id}", status_code=204, summary="Delete a task")
def delete_task(task_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tasks WHERE id = %s", (task_id,))
    existing = cursor.fetchone()

    if existing is None:
        cursor.close()
        conn.close()
        raise HTTPException(status_code=404, detail="Task not found")

    cursor.execute("DELETE FROM tasks WHERE id = %s", (task_id,))
    conn.commit()
    cursor.close()
    conn.close()
    return
