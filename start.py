"""
T&TG Trade Corp — Google Cloud Run startup script
Keep this lean — Cloud Run has a 4-minute startup timeout
"""
import os, sys, subprocess, time

print("=== T&TG Trade Corp Starting ===")
print(f"Settings: {os.environ.get('DJANGO_SETTINGS_MODULE', 'NOT SET')}")

# Wait for Cloud SQL proxy / Neon connection to be ready
time.sleep(5)

# Run migrations — retry up to 5 times with longer waits
print("\n--- Running migrations ---")
migration_ok = False
for attempt in range(5):
    print(f"  Migration attempt {attempt + 1}/5 ...")
    result = subprocess.run(
        [sys.executable, "manage.py", "migrate", "--noinput"],
        capture_output=False
    )
    if result.returncode == 0:
        print("Migrations OK")
        migration_ok = True
        break
    wait = (attempt + 1) * 5   # 5, 10, 15, 20, 25 seconds
    print(f"  Migration attempt {attempt+1} failed — retrying in {wait}s ...")
    time.sleep(wait)

if not migration_ok:
    print("WARNING: migrations could not be applied — starting anyway")

# Create cache table — non-fatal
subprocess.run([sys.executable, "manage.py", "createcachetable"], capture_output=False)

# Setup auth providers in background so gunicorn starts fast
def _bg(cmd):
    subprocess.Popen([sys.executable, "manage.py"] + cmd)

_bg(["setup_auth"])

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
    "--graceful-timeout", "30",
])
