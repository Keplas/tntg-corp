import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# ── Security ───────────────────────────────────────────────────────────────────
SECRET_KEY = os.environ.get(
    'SECRET_KEY',
    'django-insecure-tntg-trade-corp-2026-secure-key-change-in-production'
)
DEBUG = os.environ.get('DEBUG', 'True') == 'True'
ALLOWED_HOSTS = ['tntg-corp.onrender.com', 'tntgcorp.com', 'localhost', '127.0.0.1', '.onrender.com']

# ── Apps ───────────────────────────────────────────────────────────────────────
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'cloudinary_storage',
    'cloudinary',
    'core',
    'marketplace',
    'accounts',
    'services',
    'training',
]

# ── Middleware ─────────────────────────────────────────────────────────────────
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'tntg_corp.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'core.context_processors.cloudinary_status',
            ],
        },
    },
]

WSGI_APPLICATION = 'tntg_corp.wsgi.application'

# ── Database ───────────────────────────────────────────────────────────────────
DATABASE_URL = os.environ.get('DATABASE_URL', '')
if DATABASE_URL:
    import dj_database_url
    DATABASES = {'default': dj_database_url.parse(DATABASE_URL, conn_max_age=600)}
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# ── Auth ───────────────────────────────────────────────────────────────────────
AUTH_USER_MODEL = 'accounts.CustomUser'
LOGIN_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = '/accounts/dashboard/'
LOGOUT_REDIRECT_URL = '/'

# Allows login with username, email, or phone number.
AUTHENTICATION_BACKENDS = [
    'accounts.backends.FlexAuthBackend',
    'django.contrib.auth.backends.ModelBackend',
]

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ── Localisation ───────────────────────────────────────────────────────────────
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# ── Static Files ───────────────────────────────────────────────────────────────
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# ── Media / Image Storage ──────────────────────────────────────────────────────
MEDIA_ROOT = BASE_DIR / 'media'
MEDIA_URL = '/media/'

CLOUDINARY_CLOUD_NAME = os.environ.get('CLOUDINARY_CLOUD_NAME', '')
CLOUDINARY_API_KEY    = os.environ.get('CLOUDINARY_API_KEY', '')
CLOUDINARY_API_SECRET = os.environ.get('CLOUDINARY_API_SECRET', '')

USE_CLOUDINARY = all([CLOUDINARY_CLOUD_NAME, CLOUDINARY_API_KEY, CLOUDINARY_API_SECRET])

if USE_CLOUDINARY:
    import cloudinary
    cloudinary.config(
        cloud_name = CLOUDINARY_CLOUD_NAME,
        api_key    = CLOUDINARY_API_KEY,
        api_secret = CLOUDINARY_API_SECRET,
        secure     = True,
    )
    CLOUDINARY_STORAGE = {
        'CLOUD_NAME': CLOUDINARY_CLOUD_NAME,
        'API_KEY':    CLOUDINARY_API_KEY,
        'API_SECRET': CLOUDINARY_API_SECRET,
    }
    DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'
    MEDIA_URL = f'https://res.cloudinary.com/{CLOUDINARY_CLOUD_NAME}/'
else:
    DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ── Trusted origins for CSRF (required behind Render's reverse proxy) ──────────
CSRF_TRUSTED_ORIGINS = [
    'https://tntg-corp.onrender.com',
    'https://tntgcorp.com',
    'https://*.onrender.com',
]
