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
        capture_output=True,
        text=True,
    )
    if result.returncode == 0:
        print("Migrations OK")
        if result.stdout:
            print(result.stdout[-2000:])  # last 2 KB of output
        migration_ok = True
        break
    wait = (attempt + 1) * 5   # 5, 10, 15, 20, 25 seconds
    print(f"  Migration attempt {attempt+1} failed (exit {result.returncode}) — retrying in {wait}s ...")
    if result.stdout:
        print("STDOUT:", result.stdout[-1000:])
    if result.stderr:
        print("STDERR:", result.stderr[-1000:])
    time.sleep(wait)

if not migration_ok:
    print("ERROR: all 5 migration attempts failed — starting anyway (tables may be missing)")

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
