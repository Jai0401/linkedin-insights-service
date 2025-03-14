# Dockerfile
FROM python:3.9-slim-buster

WORKDIR /app

# Install system dependencies required for mysqlclient
RUN apt-get update && apt-get install -y \
    build-essential \
    pkg-config \
    default-libmysqlclient-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY ./app ./app
COPY ./app/main.py ./

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]