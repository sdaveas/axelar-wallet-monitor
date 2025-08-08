# syntax=docker/dockerfile:1

FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install runtime deps
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Add source code
COPY app/ /app/

# Create data directory for volume mount
RUN mkdir -p /app/data

ENTRYPOINT ["python", "/app/main.py"]

