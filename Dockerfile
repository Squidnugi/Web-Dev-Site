# Use Python 3.12 as the base image
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8080 \
    FLASK_ENV=production

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file first to leverage Docker cache
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt gunicorn

# Copy the rest of the application
COPY . .

# Expose the port fly.io expects
EXPOSE 8080

# Command to run the application using run.py
CMD gunicorn --bind 0.0.0.0:8080 run:app