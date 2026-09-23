FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT=8080
ENV DJANGO_SETTINGS_MODULE=tntg_corp.settings_gcloud

RUN apt-get update && apt-get install -y gcc libpq-dev && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt gunicorn psycopg2-binary

COPY . .

EXPOSE 8080

CMD python manage.py migrate --noinput && \
    python manage.py collectstatic --noinput || true && \
    exec gunicorn tntg_corp.wsgi --workers 2 --timeout 120 --bind 0.0.0.0:$PORT
