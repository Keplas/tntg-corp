import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tntg_corp.settings_gcloud')
application = get_wsgi_application()
