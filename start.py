"""
T&TG Trade Corp — Google Cloud Run startup script
Runs migrations then starts gunicorn
"""
import os
import sys
import subprocess

print("=== T&TG Trade Corp Starting on Google Cloud ===")
print(f"Settings: {os.environ.get('DJANGO_SETTINGS_MODULE')}")
print(f"DB Host: {os.environ.get('DB_HOST')}")
print(f"DB Name: {os.environ.get('DB_NAME')}")

# Step 1: Run migrations
print("\n--- Running database migrations ---")
result = subprocess.run(
    [sys.executable, "manage.py", "migrate", "--noinput", "--verbosity=2"],
    capture_output=False
)

if result.returncode != 0:
    print("ERROR: Migrations failed. Exiting.")
    sys.exit(1)

print("--- Migrations complete ---\n")

# Step 2: Collect static files
print("--- Collecting static files ---")
subprocess.run(
    [sys.executable, "manage.py", "collectstatic", "--noinput"],
    capture_output=False
)

# Step 3: Start gunicorn
print("--- Starting Gunicorn ---")
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
