FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT=8080
ENV DJANGO_SETTINGS_MODULE=tntg_corp.settings_gcloud

RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    curl \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt gunicorn psycopg2-binary

COPY . .

RUN printf '#!/bin/bash\n\
set -e\n\
echo "=== T&TG Trade Corp Starting on Google Cloud ==="\n\
echo "Settings: $DJANGO_SETTINGS_MODULE"\n\
echo "DB Host: $DB_HOST"\n\
echo "DB Name: $DB_NAME"\n\
echo "DB User: $DB_USER"\n\
\n\
# Create database if it does not exist\n\
echo "Ensuring database exists..."\n\
PGPASSWORD=$DB_PASSWORD psql \\\n\
    -h "$DB_HOST" \\\n\
    -U "$DB_USER" \\\n\
    -tc "SELECT 1 FROM pg_database WHERE datname = '"'"'$DB_NAME'"'"'" \\\n\
    | grep -q 1 || PGPASSWORD=$DB_PASSWORD psql \\\n\
    -h "$DB_HOST" \\\n\
    -U "$DB_USER" \\\n\
    -c "CREATE DATABASE $DB_NAME;" || echo "DB creation skipped"\n\
\n\
echo "Running migrations..."\n\
python manage.py migrate --noinput || echo "Migration warning"\n\
\n\
echo "Collecting static files..."\n\
python manage.py collectstatic --noinput || echo "Collectstatic warning"\n\
\n\
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
