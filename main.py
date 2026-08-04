from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import sqlite3

def get_db_connection():
    conn = sqlite3.connect("tasks.db")
    conn.row_factory = sqlite3.Row
    return conn

class Task(BaseModel):
    title: str

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    done: Optional[bool] = None

app = FastAPI()

def get_db_connection():
    conn = sqlite3.connect("tasks.db")
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            done BOOLEAN NOT NULL DEFAULT 0
        )
    """)

    cursor.execute("SELECT COUNT(*) FROM tasks")
    count = cursor.fetchone()[0]

    if count == 0:
        cursor.execute("INSERT INTO tasks (title, done) VALUES (?, ?)", ("Complete stage 0 and commit to git", 1))
        cursor.execute("INSERT INTO tasks (title, done) VALUES (?, ?)", ("Complete stage 1 and commit to git", 1))
        cursor.execute("INSERT INTO tasks (title, done) VALUES (?, ?)", ("Complete stage 2 and commit to git", 0))
    conn.commit()
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

@app.get("/tasks", summary="List all tasks")
def get_tasks():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tasks")
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
    found_task = None
    for task in tasks:
        if task["id"] == task_id:
            found_task = task
            break

    if found_task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    if update_data.title is not None:
        if not update_data.title.strip():
            raise HTTPException(status_code=400, detail="Title cannot be empty")
        found_task["title"] = update_data.title

    if update_data.done is not None:
        found_task["done"] = update_data.done

    return found_task


@app.delete("/tasks/{task_id}", status_code=204, summary="Delete a task")
def delete_task(task_id: int):
    found_task = None
    for task in tasks:
        if task["id"] == task_id:
            found_task = task
            break

    if found_task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    tasks.remove(found_task)
    return