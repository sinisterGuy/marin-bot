FROM python:3.9-slim
WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y ffmpeg && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
CMD ["python", "main.py"]

VOLUME /app/data  # Stores SQLite file persistently

# Set memory limits
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1

# Limit Python memory usage
CMD ["python", "-O", "main.py"]  # -O for optimizations