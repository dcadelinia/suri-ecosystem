FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy and install python library modules
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Create the internal data directory explicitly so SQLite has write-access
RUN mkdir -p /data

# Bundle project files
COPY . .

EXPOSE 8080

# Execute direct module call matching your main entry script structure
CMD ["python", "-m", "uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8080"]
