# ==========================================
# FLYRANK AI — ASSIGNMENT W2/W3: TASK CRUD API & DATABASE STACK
# ==========================================

# ==========================================
# TODO 0 — Imports & Environment Setup
# ==========================================

# PSEUDOCODE:
# 1. Import required modules:
#    - Operating system and typing (os, Optional)
#    - Environment variable reader (load_dotenv from python-dotenv)
#    - Web framework (FastAPI, HTTPException, status)
#    - Data validation library (BaseModel from pydantic)
#    - PostgreSQL database adapter (psycopg2, RealDictCursor)
# 2. Load environment variables from .env file:
#    - Read DATABASE_URL

import os
from typing import Optional
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel
import psycopg2
from psycopg2.extras import RealDictCursor

# Load environment variables from .env file
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")


# ==========================================
# TODO 1 — Pydantic Request Schemas
# ==========================================

# PSEUDOCODE:
# Define data models for task creation and task updates:
# - Task (creation): requires title (non-empty string)
# - TaskUpdate (partial update): optional title and optional done boolean flag

class Task(BaseModel):
    title: str

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    done: Optional[bool] = None


# ==========================================
# TODO 2 — Database Connection & Table Initialization
# ==========================================

# PSEUDOCODE:
# 1. Helper function `get_db_connection`:
#    - Establish connection to PostgreSQL using DATABASE_URL and RealDictCursor.
# 2. Function `init_db`:
#    - Execute `CREATE TABLE IF NOT EXISTS tasks (id SERIAL PRIMARY KEY, title TEXT NOT NULL, done BOOLEAN NOT NULL DEFAULT FALSE)`.
#    - Check if table is empty; seed starter tasks if count == 0.

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

# Initialize PostgreSQL table & seed starter data if empty
init_db()

app = FastAPI(title="Task Management CRUD API")


# ==========================================
# TODO 3 — Root & Health Check Endpoints
# ==========================================

# PSEUDOCODE:
# Route: GET "/" -> returns API name, version, and endpoints.
# Route: GET "/health" -> returns {"status": "ok"}.

@app.get("/", summary="Root endpoint - API Information")
def read_root():
    return {
        "name": "Task API",
        "version": "1.0",
        "endpoints": ["/tasks"]
    }

@app.get("/health", summary="Health check")
def health():
    return {"status": "ok"}


# ==========================================
# TODO 4 — List Tasks & Compute Task Statistics
# ==========================================

# PSEUDOCODE:
# Route: GET "/tasks" -> accepts search, done filter, and sort order parameters.
# Route: GET "/stats" -> returns total_tasks, completed_tasks, and pending_tasks counts.

@app.get("/tasks", summary="List all tasks with optional search, filter, and sort")
def get_tasks(search: Optional[str] = None, done: Optional[bool] = None, sort: Optional[str] = None):
    conn = get_db_connection()
    cursor = conn.cursor()

    query = "SELECT * FROM tasks"
    conditions = []
    params = []

    if search is not None and search.strip():
        conditions.append("title LIKE %s")
        params.append(f"%{search.strip()}%")

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

    cursor.execute("SELECT COUNT(*) AS total FROM tasks")
    total = cursor.fetchone()["total"]

    cursor.execute("SELECT COUNT(*) AS completed FROM tasks WHERE done = TRUE")
    completed = cursor.fetchone()["completed"]

    cursor.execute("SELECT COUNT(*) AS pending FROM tasks WHERE done = FALSE")
    pending = cursor.fetchone()["pending"]

    cursor.close()
    conn.close()

    return {
        "total_tasks": total,
        "completed_tasks": completed,
        "pending_tasks": pending
    }


# ==========================================
# TODO 5 — Read Single Task by ID
# ==========================================

# PSEUDOCODE:
# Route: GET "/tasks/{task_id}"
# Input: task_id integer path parameter.
# Process: Query task by ID.
# Error Case: If row is None -> raise 404 HTTPException("Task not found").

@app.get("/tasks/{task_id}", summary="Get a single task by ID")
def get_task(task_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tasks WHERE id = %s", (task_id,))
    row = cursor.fetchone()
    cursor.close()
    conn.close()

    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

    return {
        "id": row["id"],
        "title": row["title"],
        "done": bool(row["done"])
    }


# ==========================================
# TODO 6 — Create New Task
# ==========================================

# PSEUDOCODE:
# Route: POST "/tasks"
# Input: Task body
# Validation: If title is empty/whitespace -> raise 400 HTTPException.
# Output Status: 201 CREATED

@app.post("/tasks", status_code=status.HTTP_201_CREATED, summary="Create a new task")
def create_task(task: Task):
    if not task.title.strip():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Title cannot be empty")

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO tasks (title, done) VALUES (%s, %s) RETURNING *",
        (task.title, False)
    )
    new_task = cursor.fetchone()
    conn.commit()
    cursor.close()
    conn.close()

    return {
        "id": new_task["id"],
        "title": new_task["title"],
        "done": bool(new_task["done"])
    }


# ==========================================
# TODO 7 — Update Existing Task
# ==========================================

# PSEUDOCODE:
# Route: PUT "/tasks/{task_id}"
# Input: task_id path parameter, TaskUpdate body
# Process: Fetch task; if None -> raise 404. Update title/done fields dynamically.

@app.put("/tasks/{task_id}", summary="Update an existing task")
def update_task(task_id: int, update_data: TaskUpdate):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM tasks WHERE id = %s", (task_id,))
    task = cursor.fetchone()

    if task is None:
        cursor.close()
        conn.close()
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

    new_title = task["title"]
    new_done = task["done"]

    if update_data.title is not None:
        if not update_data.title.strip():
            cursor.close()
            conn.close()
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Title cannot be empty")
        new_title = update_data.title

    if update_data.done is not None:
        new_done = update_data.done

    cursor.execute(
        "UPDATE tasks SET title = %s, done = %s WHERE id = %s",
        (new_title, new_done, task_id)
    )
    conn.commit()
    cursor.close()
    conn.close()

    return {
        "id": task_id,
        "title": new_title,
        "done": bool(new_done)
    }


# ==========================================
# TODO 8 — Delete Task
# ==========================================

# PSEUDOCODE:
# Route: DELETE "/tasks/{task_id}"
# Process: Check task existence; if None -> 404; else DELETE. Status code: 204 NO CONTENT.

@app.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete a task")
def delete_task(task_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM tasks WHERE id = %s", (task_id,))
    task = cursor.fetchone()

    if task is None:
        cursor.close()
        conn.close()
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

    cursor.execute("DELETE FROM tasks WHERE id = %s", (task_id,))
    conn.commit()
    cursor.close()
    conn.close()
    return