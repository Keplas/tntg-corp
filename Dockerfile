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

RUN printf '#!/bin/bash\n\
set -e\n\
echo "=== T&TG Starting on Google Cloud ==="\n\
echo "Settings: $DJANGO_SETTINGS_MODULE"\n\
echo "DB Host: $DB_HOST"\n\
echo "DB Name: $DB_NAME"\n\
echo "DB User: $DB_USER"\n\
echo "Running migrations..."\n\
python manage.py migrate --noinput 2>&1\n\
echo "Migration exit code: $?"\n\
echo "Collecting static files..."\n\
python manage.py collectstatic --noinput 2>&1 || true\n\
echo "Starting gunicorn..."\n\
exec gunicorn tntg_corp.wsgi \\\n\
    --workers 2 \\\n\
    --timeout 120 \\\n\
    --bind 0.0.0.0:$PORT \\\n\
    --log-file - \\\n\
    --access-logfile -\n\
' > /app/start.sh

RUN chmod +x /app/start.sh

EXPOSE 8080

CMD ["/app/start.sh"]
