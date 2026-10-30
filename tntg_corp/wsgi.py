import os
import pathlib
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tntg_corp.settings_gcloud')

_django_app = get_wsgi_application()

# ── Apple Pay domain verification ──────────────────────────────────────────────
# Served at the WSGI layer — before Django middleware — so nothing can block it.
_APPLE_PAY_PATH = '/.well-known/apple-developer-merchantid-domain-association'
_APPLE_PAY_FILE = (
    pathlib.Path(__file__).resolve().parent.parent
    / 'public' / '.well-known' / 'apple-developer-merchantid-domain-association'
)


def application(environ, start_response):
    if environ.get('PATH_INFO') == _APPLE_PAY_PATH:
        try:
            content = _APPLE_PAY_FILE.read_bytes()
            start_response('200 OK', [
                ('Content-Type', 'application/octet-stream'),
                ('Content-Length', str(len(content))),
                ('Cache-Control', 'no-cache'),
            ])
            return [content]
        except Exception as exc:
            body = f'Apple Pay file error: {exc}'.encode()
            start_response('500 Internal Server Error', [
                ('Content-Type', 'text/plain'),
                ('Content-Length', str(len(body))),
            ])
            return [body]
    return _django_app(environ, start_response)
