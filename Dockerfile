FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT=8080
ENV DJANGO_SETTINGS_MODULE=tntg_corp.settings_gcloud

RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt gunicorn psycopg2-binary

COPY . .

# Startup script - runs migrations then starts server
RUN printf '#!/bin/bash\nset -e\necho "=== Running migrations ==="\npython manage.py migrate --noinput\necho "=== Collecting static files ==="\npython manage.py collectstatic --noinput\necho "=== Starting server ==="\nexec gunicorn tntg_corp.wsgi --workers 2 --timeout 120 --bind 0.0.0.0:$PORT --log-file -\n' > /app/start.sh

RUN chmod +x /app/start.sh

EXPOSE 8080

CMD ["/app/start.sh"]
