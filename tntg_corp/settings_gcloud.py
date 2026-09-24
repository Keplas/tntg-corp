"""
T&TG Trade Corporation — Google Cloud Run Settings
Extends base settings.py with Cloud-specific overrides.
"""
from .settings import *
import os

# ── Security ──────────────────────────────────────────────────────────────────
DEBUG = True  # Temp: show errors
SECRET_KEY = os.environ.get('SECRET_KEY', SECRET_KEY)
ALLOWED_HOSTS = [
    'tomtradecorp.com',
    'www.tomtradecorp.com',
    '.run.app',
    '127.0.0.1',
    'localhost',
]

CSRF_TRUSTED_ORIGINS = [
    'https://tomtradecorp.com',
    'https://www.tomtradecorp.com',
    'https://*.run.app',
]

# ── Database — Cloud SQL (PostgreSQL) ─────────────────────────────────────────
# Cloud SQL Database — overrides base settings.py
DATABASES = {
    'default': {
        'ENGINE':   'django.db.backends.postgresql',
        'NAME':     os.environ.get('DB_NAME',     'tntg_db'),
        'USER':     os.environ.get('DB_USER',     'postgres'),
        'PASSWORD': os.environ.get('DB_PASSWORD', ''),
        'HOST':     os.environ.get('DB_HOST',     '/cloudsql/tomgrouptrade:us-east1:tntg-db'),
        'PORT':     os.environ.get('DB_PORT',     '5432'),
    }
}

# ── Static Files — Cloud Storage ──────────────────────────────────────────────
GCS_BUCKET = os.environ.get('GCS_BUCKET_NAME', '')

if GCS_BUCKET:
    DEFAULT_FILE_STORAGE    = 'storages.backends.gcloud.GoogleCloudStorage'
    STATICFILES_STORAGE     = 'storages.backends.gcloud.GoogleCloudStorage'
    GS_BUCKET_NAME          = GCS_BUCKET
    GS_DEFAULT_ACL          = 'publicRead'
    STATIC_URL              = f'https://storage.googleapis.com/{GCS_BUCKET}/static/'
    MEDIA_URL               = f'https://storage.googleapis.com/{GCS_BUCKET}/media/'
else:
    # WhiteNoise fallback if no GCS bucket yet
    STATICFILES_STORAGE = 'whitenoise.storage.StaticFilesStorage'

# ── Email ─────────────────────────────────────────────────────────────────────
EMAIL_BACKEND       = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST          = 'smtp.gmail.com'
EMAIL_PORT          = 587
EMAIL_USE_TLS       = True
EMAIL_HOST_USER     = os.environ.get('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '')

# ── Cloudinary ────────────────────────────────────────────────────────────────
CLOUDINARY_CLOUD_NAME = os.environ.get('CLOUDINARY_CLOUD_NAME', '')
CLOUDINARY_API_KEY    = os.environ.get('CLOUDINARY_API_KEY', '')
CLOUDINARY_API_SECRET = os.environ.get('CLOUDINARY_API_SECRET', '')

# ── Logging ───────────────────────────────────────────────────────────────────
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {'class': 'logging.StreamHandler'},
    },
    'root': {
        'handlers': ['console'],
        'level': 'DEBUG',
    },
}

# Tell Django it is behind HTTPS proxy (Cloud Run)
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# ── Security Headers ──────────────────────────────────────────────────────────
SECURE_SSL_REDIRECT              = False  # Cloud Run handles SSL externally
SECURE_HSTS_SECONDS              = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS   = True
SESSION_COOKIE_SECURE            = True
CSRF_COOKIE_SECURE               = True
