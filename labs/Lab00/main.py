from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello WorlClass"}

# In-memory data store
tasks = {}
next_id = 1

# Pydantic model for task request validation
class Task(BaseModel):
    title: str
    description: str | None = None
    completed: bool = False


# RESTFul endpoints
# GET all tasks
@app.get("/tasks", response_model=List[Task])
def get_tasks():
    return list(tasks.values())

# POST create a task
@app.post("/tasks", status_code=201)
def create_task(task: Task):
    global next_id
    tasks[next_id] = task
    next_id += 1
    return task

# GET one task
@app.get("/tasks/{task_id}", response_model=Task)
def read_task(task_id: int):
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    return tasks[task_id]

# PUT update a task
@app.put("/tasks/{task_id}", response_model=Task)
def update_task(task_id: int, task: Task):
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    tasks[task_id] = task
    return task


# DELETE a task
@app.delete("/tasks/{task_id}", status_code=204)
def delete_task(task_id: int):
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    del tasks[task_id]
