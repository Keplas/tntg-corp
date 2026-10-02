"""Minimal settings for Docker build-time operations"""
from tntg_corp.settings import *

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': '/tmp/build.db',
    }
}
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'
CLOUDINARY_STORAGE = {}
DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'
