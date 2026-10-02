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

# Collect static files at build time (faster startup)
RUN DJANGO_SETTINGS_MODULE=tntg_corp.settings \
    SECRET_KEY=build-time-key \
    DATABASE_URL=sqlite:///tmp/build.db \
    python manage.py collectstatic --noinput || echo "collectstatic skipped"

EXPOSE 8080

CMD ["python", "start.py"]
