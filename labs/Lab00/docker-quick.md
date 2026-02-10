Here’s a **minimal FastAPI server that returns a simple response** and how to **dockerize it** so you can run it in a Docker container.

---

## 1) FastAPI app (simple “Hello World”)

Create a file `main.py` with:

```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Hello World"}
```

This defines a FastAPI app with one route `/` that returns JSON. ([fastapi.tiangolo.com][1])

---

## 2) Requirements file

Create `requirements.txt` next to `main.py`:

```
fastapi
uvicorn[standard]
```

---

## 3) Dockerfile

In the same folder, create a `Dockerfile`:

```dockerfile
# Use official Python base image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy local code
COPY . .

# Expose port 8000
EXPOSE 8000

# Run FastAPI via Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

This image installs Python dependencies and runs the FastAPI app using Uvicorn. ([Medium][2])

---

## 4) Build and run with Docker

### Build the image

```bash
docker build -t fastapi-simple .
```

### Run the container

```bash
docker run -p 8000:8000 fastapi-simple
```

Now open your browser at `http://localhost:8000/` — you should see:

```json
{"message":"Hello World"}
```

---

## 5) (Optional) Using an official FastAPI base image

FastAPI docs also show how to use a ready Docker image like `tiangolo/uvicorn-gunicorn-fastapi` which bundles Uvicorn + Gunicorn and is convenient for production: ([fastapi.tiangolo.com][1])

```dockerfile
FROM tiangolo/uvicorn-gunicorn-fastapi:python3.11
COPY . /app
```

---

That’s it — a simple FastAPI server that returns a response, containerized with Docker! 🚀

[1]: https://fastapi.tiangolo.com/deployment/docker/?utm_source=chatgpt.com "FastAPI in Containers - Docker"
[2]: https://medium.com/%40alidu143/containerizing-fastapi-app-with-docker-a-comprehensive-guide-416521b2457c?utm_source=chatgpt.com "Containerizing FastAPI App with Docker"
