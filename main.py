from fastapi import FastAPI, HTTPException

app = FastAPI()

@app.get("/")
def read_root():
    return {

        "name": "Task API",
        "version": "1.0",
        "endpoints": ["/tasks"]

    }

@app.get("/health")
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

@app.get("/tasks")
def get_tasks():
    return tasks

@app.get("/tasks/{task_id}")
def get_task(task_id: int): 
    for task in tasks:
        if task["id"] == task_id:
            return task
    raise HTTPException(status_code=404, detail="Task not found")