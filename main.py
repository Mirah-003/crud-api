import os
from typing import Optional
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import psycopg2
from psycopg2.extras import RealDictCursor

# Load environment variables from .env file
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

class Task(BaseModel):
    title: str

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    done: Optional[bool] = None

app = FastAPI()

# Establish database connection using psycopg2
def get_db_connection():
    conn = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
    return conn

# Initialize PostgreSQL table & seed starter data if empty
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
    conn.commit()

    cursor.execute("SELECT COUNT(*) AS count FROM tasks")
    count = cursor.fetchone()["count"]

    if count == 0:
        cursor.execute("INSERT INTO tasks (title, done) VALUES (%s, %s)", ("Complete stage 0 and commit to git", True))
        cursor.execute("INSERT INTO tasks (title, done) VALUES (%s, %s)", ("Complete stage 1 and commit to git", True))
        cursor.execute("INSERT INTO tasks (title, done) VALUES (%s, %s)", ("Complete stage 2 and commit to git", False))
        conn.commit()

    cursor.close()
    conn.close()

init_db()

@app.get("/", summary="Root endpoint - API Information")
def read_root():
    return {

        "name": "Task API",
        "version": "1.0",
        "endpoints": ["/tasks"]

    }


@app.get("/health", summary="Health check")
def health():
    return { 
        
        "status": "ok"
    }

@app.get("/tasks", summary="List all tasks with optional search, filter, and sort")
def get_tasks(search: Optional[str] = None, done: Optional[bool] = None, sort: Optional[str] = None):
    conn = get_db_connection()
    cursor = conn.cursor()

    query = "SELECT * FROM tasks"
    conditions = []
    params = []

    if search is not None and search.strip():
        conditions.append("title LIKE ?")
        params.append(f"%{search.strip()}%")

    if done is not None:
        conditions.append("done = ?")
        params.append(1 if done else 0)

    if conditions:
        query += " WHERE " + " AND ".join(conditions)

    if sort == "title":
        query += " ORDER BY title ASC"
    else:
        query += " ORDER BY id ASC"

    cursor.execute(query, tuple(params))
    rows = cursor.fetchall()
    conn.close()

    task_list = []
    for row in rows:
        task_list.append({
            "id": row["id"],
            "title": row["title"],
            "done": bool(row["done"])
        })
    return task_list

@app.get("/stats", summary="Get task statistics")
def get_stats():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM tasks")
    total = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM tasks WHERE done = 1")
    completed = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM tasks WHERE done = 0")
    pending = cursor.fetchone()[0]

    conn.close()

    return {
        "total_tasks": total,
        "completed_tasks": completed,
        "pending_tasks": pending
    }

@app.get("/tasks/{task_id}", summary="Get a single task by ID")
def get_task(task_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
    row = cursor.fetchone()
    conn.close()
    if row is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return {
        "id": row["id"],
        "title": row["title"],
        "done": bool(row["done"])
    }

@app.post("/tasks", status_code=201, summary="Create a new task")
def create_task(task: Task):
    if not task.title.strip():
        raise HTTPException(status_code=400, detail="Title cannot be empty")

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO tasks (title, done) VALUES (?, ?)", (task.title, 0))
    conn.commit()

    new_id = cursor.lastrowid
    conn.close()

    return {
        "id": new_id,
        "title": task.title,
        "done": False
    }

@app.put("/tasks/{task_id}", summary="Update an existing task")
def update_task(task_id: int, update_data: TaskUpdate):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
    task = cursor.fetchone()

    if task is None:
        conn.close()
        raise HTTPException(status_code=404, detail="Task not found")

    new_title = task["title"]
    new_done = task["done"]

    if update_data.title is not None:
        if not update_data.title.strip():
            conn.close()
            raise HTTPException(status_code=400, detail="Title cannot be empty")
        new_title = update_data.title

    if update_data.done is not None:
        new_done = 1 if update_data.done else 0

    cursor.execute(
        "UPDATE tasks SET title = ?, done = ? WHERE id = ?",
        (new_title, new_done, task_id)
    )
    conn.commit()
    conn.close()

    return {
        "id": task_id,
        "title": new_title,
        "done": bool(new_done)
    }


@app.delete("/tasks/{task_id}", status_code=204, summary="Delete a task")
def delete_task(task_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
    task = cursor.fetchone()

    if task is None:
        conn.close()
        raise HTTPException(status_code=404, detail="Task not found")

    cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    conn.commit()
    conn.close()
    return