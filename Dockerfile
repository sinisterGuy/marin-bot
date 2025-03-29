FROM python:3.9-slim
WORKDIR /app

# Install system deps
RUN apt-get update && \
    apt-get install -y ffmpeg build-essential && \
    rm -rf /var/lib/apt/lists/*

# Environment config
ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=off \
    PYTHONDONTWRITEBYTECODE=1

# Install Python deps
COPY requirements.txt .
RUN pip install --user -r requirements.txt

# Copy app
COPY . .

# Runtime config
VOLUME /app/data
CMD ["python", "main.py"]