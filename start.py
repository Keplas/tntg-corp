"""
T&TG Trade Corp — Google Cloud Run startup script
"""
import os
import sys
import subprocess

print("=== T&TG Trade Corp Starting on Google Cloud ===")
print(f"Settings: {os.environ.get('DJANGO_SETTINGS_MODULE', 'NOT SET')}")
print(f"DB Host:  {os.environ.get('DB_HOST', 'NOT SET')}")
print(f"DB Name:  {os.environ.get('DB_NAME', 'NOT SET')}")
print(f"DB User:  {os.environ.get('DB_USER', 'NOT SET')}")

# Run migrations
print("\n--- Running database migrations ---")
result = subprocess.run(
    [sys.executable, "manage.py", "migrate", "--noinput"],
    capture_output=False
)
print(f"Migration exit code: {result.returncode}")

# Collect static files
print("\n--- Collecting static files ---")
subprocess.run(
    [sys.executable, "manage.py", "collectstatic", "--noinput", "--clear"],
    capture_output=False
)

# Start gunicorn
print("\n--- Starting Gunicorn ---")
port = os.environ.get("PORT", "8080")
os.execvp("gunicorn", [
    "gunicorn",
    "tntg_corp.wsgi",
    "--workers", "2",
    "--timeout", "120",
    "--bind", f"0.0.0.0:{port}",
    "--log-file", "-",
    "--access-logfile", "-",
])
