import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# ── Security ───────────────────────────────────────────────────────────────────
SECRET_KEY = os.environ.get(
    'SECRET_KEY',
    'django-insecure-tntg-trade-corp-2026-secure-key-change-in-production'
)
DEBUG = os.environ.get('DEBUG', 'True') == 'True'
ALLOWED_HOSTS = [
    '.run.app',
    'tomtradecorp.com','tomtradecorp.com', 'tntgcorp.com', 'localhost', '127.0.0.1', '.onrender.com']

# ── Apps ───────────────────────────────────────────────────────────────────────
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    # Third party
    'allauth',
    'allauth.account',
    'allauth.mfa',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
    'allauth.socialaccount.providers.microsoft',
    'axes',
    'cloudinary_storage',
    'cloudinary',
    # Local
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
    'allauth.account.middleware.AccountMiddleware',
    'axes.middleware.AxesMiddleware',
    'accounts.middleware.EnforceMFAForStaffMiddleware',
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
                'core.context_processors.social_links',
                'core.context_processors.notifications_ctx',
            ],
        },
    },
]

WSGI_APPLICATION = 'tntg_corp.wsgi.application'

# ── Database ───────────────────────────────────────────────────────────────────
DATABASE_URL = os.environ.get('DATABASE_URL', '')
if DATABASE_URL and '://' in DATABASE_URL:
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
    'https://tomtradecorp.com',
    'https://tntgcorp.com',
    'https://*.onrender.com',
]

# ── Social Media Links (set these on Render when ready) ─────────────────────
# Add these as Environment Variables on Render dashboard to activate each icon
SOCIAL_LINKEDIN  = os.environ.get('SOCIAL_LINKEDIN',  '')
SOCIAL_FACEBOOK  = os.environ.get('SOCIAL_FACEBOOK',  '')
SOCIAL_INSTAGRAM = os.environ.get('SOCIAL_INSTAGRAM', '')
SOCIAL_TIKTOK    = os.environ.get('SOCIAL_TIKTOK',    '')
SOCIAL_WHATSAPP  = os.environ.get('SOCIAL_WHATSAPP',  'https://wa.me/14168323512')

# ── Open Exchange Rates API ──────────────────────────────────────────────────
# Sign up free at https://openexchangerates.org — add key to Render env vars
EXCHANGE_RATES_API_KEY = os.environ.get('EXCHANGE_RATES_API_KEY', '')

# ── Cache (1-hour in-memory — reduces API calls to ~24/day) ─────────────────
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'tntg-cache',
        'TIMEOUT': 3600,  # 1 hour
    }
}

# ── Site ID (required by allauth) ─────────────────────────────────────────────
SITE_ID = 1

# ── Authentication backends ───────────────────────────────────────────────────
AUTHENTICATION_BACKENDS = [
    'axes.backends.AxesStandaloneBackend',
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]

# ── django-allauth config ─────────────────────────────────────────────────────
ACCOUNT_LOGIN_METHODS           = {'email', 'username'}
ACCOUNT_EMAIL_VERIFICATION           = 'none'     # Re-enable to 'optional' once Gmail app password is fixed
ACCOUNT_SESSION_REMEMBER        = True
ACCOUNT_UNIQUE_EMAIL            = True
ACCOUNT_LOGIN_ON_EMAIL_CONFIRMATION = True
ACCOUNT_SIGNUP_FIELDS = [
    'first_name',
    'last_name',
    'email*',
    'username*',
    'password1*',
    'password2*',
]
ACCOUNT_ADAPTER             = 'accounts.adapters.CustomAccountAdapter'
ACCOUNT_FORMS               = {'signup': 'accounts.forms.CustomSignupForm'}
SOCIALACCOUNT_AUTO_SIGNUP   = True
SOCIALACCOUNT_EMAIL_REQUIRED = True
SOCIALACCOUNT_EMAIL_VERIFICATION = "none"  # Google already verifies
SOCIALACCOUNT_ADAPTER       = 'accounts.adapters.CustomSocialAccountAdapter'
SOCIALACCOUNT_LOGIN_ON_GET   = True              # Skip extra confirm step after OAuth
ACCOUNT_DEFAULT_HTTP_PROTOCOL = 'https'

# ── MFA / TOTP config ─────────────────────────────────────────────────────────
MFA_TOTP_PERIOD           = 30
MFA_TOTP_DIGITS           = 6
MFA_TOTP_ISSUER           = 'T&TG Trade Corporation'
MFA_RECOVERY_CODE_COUNT   = 8

# ── django-axes config ────────────────────────────────────────────────────────
AXES_FAILURE_LIMIT          = 5
AXES_COOLOFF_TIME           = 1          # 1 hour lockout
AXES_RESET_ON_SUCCESS       = True
AXES_LOCKOUT_TEMPLATE       = 'accounts/lockout.html'
AXES_ENABLE_ADMIN           = True
AXES_VERBOSE                = False

# ── Role groups ───────────────────────────────────────────────────────────────
TNTG_GROUPS = ['Admin', 'Staff', 'B2B Partner', 'Consumer']

# ── Loyalty and Account Security ─────────────────────────────────────────────
ACCOUNT_EMAIL_NOTIFICATIONS     = True   # Email on login, password change, new device
MFA_SUPPORTED_TYPES             = ['totp', 'recovery_codes']
MFA_TOTP_PERIOD                 = 30
MFA_EMAIL_VERIFICATION_REQUIRED = False  # Do not block 2FA setup on email verification status
MFA_PASSKEY_LOGIN_ENABLED       = False  # Enable when WebAuthn is configured

# Rate limiting (django-axes + allauth)
ACCOUNT_RATE_LIMITS = {
    'login_failed':     '5/5m',   # 5 failures per 5 minutes
    'signup':           '5/h',    # 5 signups per hour per IP
    'send_email':       '3/5m',   # 3 emails per 5 minutes
    'password_reset':   '3/h',    # 3 reset requests per hour
    'change_password':  '3/h',
    'confirm_login_code': '3/5m',
}

# Loyalty fraud controls
LOYALTY_DAILY_REDEEM_LIMIT      = 10000  # Max points redeemable per day
LOYALTY_DAILY_TXN_LIMIT         = 5      # Max transactions per day
LOYALTY_COOLOFF_HOURS           = 48     # Hours before loyalty use after account changes
LOYALTY_REAUTH_WINDOW           = 600    # Seconds (10 min) before re-auth required
