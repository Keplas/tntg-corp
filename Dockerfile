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
echo "=== T&TG Trade Corp Starting ==="\n\
echo "Running migrations..."\n\
python manage.py migrate --noinput\n\
if [ $? -eq 0 ]; then\n\
    echo "Migrations completed successfully"\n\
else\n\
    echo "Migration failed - check logs"\n\
    exit 1\n\
fi\n\
echo "Collecting static files..."\n\
python manage.py collectstatic --noinput || echo "Collectstatic warning"\n\
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
