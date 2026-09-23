"""
T&TG Trade Corp — Google Cloud Run startup script
"""
import os, sys, subprocess, time

print("=== T&TG Trade Corp Starting on Google Cloud ===")
print(f"Settings: {os.environ.get('DJANGO_SETTINGS_MODULE', 'NOT SET')}")
print(f"DB Host:  {os.environ.get('DB_HOST', 'NOT SET')}")
print(f"DB Name:  {os.environ.get('DB_NAME', 'NOT SET')}")

# Wait for Cloud SQL proxy to be ready
print("\n--- Waiting 3s for Cloud SQL proxy ---")
time.sleep(3)

# Run migrations with retry
for attempt in range(3):
    print(f"\n--- Migration attempt {attempt + 1}/3 ---")
    result = subprocess.run(
        [sys.executable, "manage.py", "migrate", "--noinput", "--verbosity=1"],
        capture_output=False
    )
    print(f"Exit code: {result.returncode}")
    if result.returncode == 0:
        print("--- Migrations successful ---")
        break
    print(f"--- Migration attempt {attempt + 1} failed, waiting 5s ---")
    time.sleep(5)

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
    "gunicorn", "tntg_corp.wsgi",
    "--workers", "2",
    "--timeout", "120",
    "--bind", f"0.0.0.0:{port}",
    "--log-file", "-",
    "--access-logfile", "-",
])
