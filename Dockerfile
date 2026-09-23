# T&TG Trade Corporation — Google Cloud Run Dockerfile
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT=8080

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir gunicorn psycopg2-binary google-cloud-storage django-storages

# Copy project
COPY . .

# Collect static files
RUN python manage.py collectstatic --noinput --settings=tntg_corp.settings_gcloud || \
    python manage.py collectstatic --noinput

# Create startup script
RUN echo '#!/bin/bash\n\
echo "Running migrations..."\n\
python manage.py migrate --noinput\n\
echo "Starting server..."\n\
exec gunicorn tntg_corp.wsgi \\\n\
    --workers 2 \\\n\
    --timeout 120 \\\n\
    --bind 0.0.0.0:$PORT \\\n\
    --log-file -' > /app/start.sh

RUN chmod +x /app/start.sh

CMD ["/app/start.sh"]
