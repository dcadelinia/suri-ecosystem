FROM python:3.10-slim 

WORKDIR /app 

### Ensure essential tooling configurations match platform compiler requirements

RUN apt-get update && apt-get install -y --no-install-recommends 
build-essential 
&& rm -rf /var/lib/apt/lists/* 

### Pre-load required package structures

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt 

### Bundle application workspace modules directly into image path runtime layers

COPY . . 

EXPOSE 8080 

CMD ["python", "-m", "uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8080"]
