FROM python:3.12.12-trixie
LABEL authors="Aris"

WORKDIR /app

# Copy requirements in working dir
COPY requirements.txt .

# Install requirements
# RUN pip install "fastapi[standard]"
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
# COPY . .
# Edit this to copy only required files
COPY main.py .
 
# Expose ports for Flask and gRPC servers
EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]