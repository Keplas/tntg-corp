"""
Background setup tasks — runs after gunicorn starts
Non-critical tasks that can run in background
"""
import os, sys, subprocess, time
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tntg_corp.settings_gcloud')

# Wait for gunicorn to be ready
time.sleep(10)

print("\n=== Running background setup tasks ===")

# Collect static files
print("--- collectstatic ---")
subprocess.run([sys.executable, "manage.py", "collectstatic", "--noinput"], capture_output=False)

# Verify emails
print("--- verify_emails ---")
subprocess.run([sys.executable, "manage.py", "verify_emails"], capture_output=False)

# Setup auth providers
print("--- setup_auth ---")
subprocess.run([sys.executable, "manage.py", "setup_auth"], capture_output=False)

# Seed data
print("--- seed_gcloud ---")
subprocess.run([sys.executable, "seed_gcloud.py"], capture_output=False)

print("=== Background setup complete ===")
