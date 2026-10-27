"""
T&TG Trade Corporation — Google Cloud Run Settings
Extends base settings.py with Cloud-specific overrides.
"""
from .settings import *
import os

# ── Security ──────────────────────────────────────────────────────────────────
DEBUG = os.environ.get('DJANGO_DEBUG', 'false').lower() == 'true'
SECRET_KEY = os.environ.get('SECRET_KEY', SECRET_KEY)
ALLOWED_HOSTS = [
    'tomtradecorp.com',
    'www.tomtradecorp.com',
    '.run.app',
    '.a.run.app',             # Cloud Run service URLs (tntg-corp-xxxx-ue.a.run.app)
    '.onrender.com',
    '127.0.0.1',
    'localhost',
]

CSRF_TRUSTED_ORIGINS = [
    'https://tomtradecorp.com',
    'https://www.tomtradecorp.com',
    'https://*.run.app',
    'https://*.a.run.app',    # Cloud Run service URLs (multi-level subdomain)
    'https://*.onrender.com',
]

# ── Database — Supabase (set DATABASE_URL in Cloud Run env vars) ──────────────
# Cloud SQL was deleted; Supabase is now the only DB.
# DATABASE_URL is parsed below after all other settings.

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
ACCOUNT_DEFAULT_HTTP_PROTOCOL = 'https'
# Force Django Sites framework to use correct domain
SITE_ID = 1
# Override allauth to use the correct domain directly
ACCOUNT_SIGNUP_REDIRECT_URL = '/accounts/dashboard/'


# ── Security Headers ──────────────────────────────────────────────────────────
SECURE_SSL_REDIRECT              = False  # Cloud Run handles SSL externally
SECURE_HSTS_SECONDS              = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS   = True
SESSION_COOKIE_SECURE            = True
CSRF_COOKIE_SECURE               = True

# ── Social Auth Credentials (set in Cloud Run env vars) ──────────────────────
SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'SCOPE': ['profile', 'email'],
        'AUTH_PARAMS': {'access_type': 'online'},
        'FETCH_USERINFO': True,
    },
    'microsoft': {
        'SCOPE': ['User.Read'],
        'AUTH_PARAMS': {'prompt': 'select_account'},
    },
}

# ── Supabase PostgreSQL (DATABASE_URL is required) ────────────────────────
import dj_database_url as _dj_db
_neon_url = os.environ.get('DATABASE_URL', '')
if _neon_url and _neon_url.startswith('postgres'):
    # conn_max_age=0  — transaction pooler (port 5432) opens a new connection
    #                   per request; persistent connections cause "prepared
    #                   statement already exists" errors on the pooler.
    DATABASES = {'default': _dj_db.parse(_neon_url, conn_max_age=0)}
    # Supabase transaction pooler does not support server-side cursors.
    DATABASES['default']['DISABLE_SERVER_SIDE_CURSORS'] = True
    # Force SSL — required by Supabase.
    DATABASES['default'].setdefault('OPTIONS', {})['sslmode'] = 'require'
else:
    # DATABASE_URL missing — refuse to start silently on the wrong DB.
    import sys
    print("[settings] FATAL: DATABASE_URL env var is not set. "
          "Set it in Cloud Run → Edit & Deploy → Variables & Secrets. "
          "Value: postgresql://postgres.<ref>:<password>@aws-1-ca-central-1.pooler.supabase.com:5432/postgres",
          file=sys.stderr)
    # Leave DATABASES as whatever base settings.py gave us (SQLite fallback)
    # so the process starts and the error is visible in Cloud Run logs.

print(f"[settings] DATABASE_URL set: {bool(_neon_url)} | DB host: {DATABASES['default'].get('HOST','?')}")

# ── Disable django-axes on Cloud Run ──────────────────────────────────────
# login_view has its own lockout logic via CustomUser.locked_until.
# Axes needs its DB tables migrated before any request — remove it from the
# request path so a failed/slow first migration doesn't 500 on sign-in.
# Set backends explicitly so FlexAuthBackend (email/phone login) is included.
MIDDLEWARE = [m for m in MIDDLEWARE if m != 'axes.middleware.AxesMiddleware']
AUTHENTICATION_BACKENDS = [
    'accounts.backends.FlexAuthBackend',           # username / email / phone
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]
# Keep 'axes' in INSTALLED_APPS so its migrations still run normally.
