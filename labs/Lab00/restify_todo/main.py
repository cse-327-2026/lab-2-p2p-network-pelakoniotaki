from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List

app = FastAPI()

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


"""
▶️ 4. Run the Server

In your terminal:

uvicorn main:app --reload


Visit http://127.0.0.1:8000
 for your API root.

FastAPI auto-generates docs:

Swagger UI: http://127.0.0.1:8000/docs

Redoc: http://127.0.0.1:8000/redoc

This gives interactive REST testing for students! 

🧠 Teaching Points (with FastAPI strengths)
✅ Type-Driven Models with Pydantic

Models like Task(BaseModel) validate incoming JSON automatically — students can see errors when fields are missing or of wrong type.

🔁 CRUD Mapping to HTTP
Action	Method	Endpoint
List tasks	GET	/tasks
Get one	GET	/tasks/{id}
Create	POST	/tasks
Update	PUT	/tasks/{id}
Delete	DELETE	/tasks/{id}

Explains mapping CRUD to REST routes.

📊 Auto-docs

Live docs let students experiment without external tools: they’ll see exactly what payloads and responses look like.

🚫 Error Handling

Show how FastAPI raises JSON errors (e.g., 404 not found) using HTTPException.


🔄 Extensions You Can Add

These make the lab more advanced when students are ready:

✅ Query parameters
Filter tasks: /tasks?completed=true

✅ Persistent storage
Swap in SQLite with SQLModel or SQLAlchemy for real data persistence.

✅ Authentication
Add simple API keys or OAuth for protected endpoints.

✅ Splitting routers
Use APIRouter to organize endpoints into modules.
"""