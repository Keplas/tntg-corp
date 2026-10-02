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

# Collect static files at build time using SQLite (no Cloud SQL needed)
RUN DJANGO_SETTINGS_MODULE=tntg_corp.settings_build \
    SECRET_KEY=build-only-not-used-in-production \
    python manage.py collectstatic --noinput 2>&1 || echo "collectstatic skipped"

EXPOSE 8080

CMD ["python", "start.py"]
