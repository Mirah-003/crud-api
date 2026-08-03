from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional

class Task(BaseModel):
    title: str

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    done: Optional[bool] = None

app = FastAPI()

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
tasks = [
    { 
        "id": 1, 
        "title": "Complete stage 0 and commit to git",   
        "done": True
    },
    { 
        "id": 2, 
        "title": "Complete stage 1 and commit to git",   
        "done": True
    },

    { 
        "id": 3, 
        "title": "Complete stage 2 and commit to git",   
        "done": False
    }
]

@app.get("/tasks", summary="List all tasks")
def get_tasks():
    return tasks


@app.get("/tasks/{task_id}", summary="Get a single task by ID")
def get_task(task_id: int): 
    for task in tasks:
        if task["id"] == task_id:
            return task
    raise HTTPException(status_code=404, detail="Task not found")

@app.post("/tasks", status_code=201, summary="Create a new task")
def create_task(task: Task):

    if not task.title.strip():
        raise HTTPException(status_code=400, detail="Title cannot be empty")

    if tasks:
        next_id = max(t["id"] for t in tasks) + 1
    else:
        next_id = 1

    new_task = {
        "id": next_id,
        "title": task.title,
        "done": False
    }

    tasks.append(new_task)
    return new_task    

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