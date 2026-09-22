# T&TG Trade Corporation — Google Cloud Run Dockerfile
FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT=8080

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set work directory
WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir gunicorn psycopg2-binary google-cloud-storage django-storages

# Copy project
COPY . .

# Collect static files
RUN python manage.py collectstatic --noinput

# Run with Gunicorn
CMD exec gunicorn tntg_corp.wsgi \
    --workers 2 \
    --timeout 120 \
    --bind 0.0.0.0:$PORT \
    --log-file -
