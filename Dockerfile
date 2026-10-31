FROM python:3.11-slim

WORKDIR /app

# Install system dependencies required for compilation tasks
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy and freeze dependencies cleanly into the container core layer
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Manually guarantee that the SQLite data folder path is writable on the container layer
RUN mkdir -p /data

# Transfer all project source assets directly into our main execution context folder
COPY . .

EXPOSE 8080

# Clean module configuration invocation ensuring python paths match perfectly
CMD ["python", "-m", "uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8080"]
