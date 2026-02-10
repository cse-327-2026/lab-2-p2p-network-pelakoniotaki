FROM python:3.12-slim

WORKDIR /app

COPY viz/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY viz /app/viz

EXPOSE 8080
CMD ["uvicorn", "viz.app:app", "--host", "0.0.0.0", "--port", "8080"]
