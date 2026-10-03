"""
T&TG Trade Corp — Google Cloud Run startup script
Keep this lean — Cloud Run has a 4-minute startup timeout
"""
import os, sys, subprocess, time

print("=== T&TG Trade Corp Starting ===")
print(f"Settings: {os.environ.get('DJANGO_SETTINGS_MODULE', 'NOT SET')}")

# Wait for Cloud SQL proxy
time.sleep(3)

# Run migrations — essential
print("\n--- Running migrations ---")
for attempt in range(3):
    result = subprocess.run(
        [sys.executable, "manage.py", "migrate", "--noinput"],
        capture_output=False
    )
    if result.returncode == 0:
        print("Migrations OK")
        break
    print(f"Migration attempt {attempt+1} failed, retrying...")
    time.sleep(5)

# Create cache table — essential
subprocess.run([sys.executable, "manage.py", "createcachetable"], capture_output=False)

# Setup auth providers (Google OAuth, Microsoft OAuth, groups)
print("\n--- Setting up auth providers ---")
subprocess.run([sys.executable, "manage.py", "setup_auth"], capture_output=False)

# Run remaining tasks in background
subprocess.Popen([sys.executable, "setup_tasks.py"])

# Start gunicorn immediately
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
