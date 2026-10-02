"""
T&TG Trade Corp — Migrate data from Cloud SQL to Neon PostgreSQL
Run this once after Neon is set up
"""
import os, sys, django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tntg_corp.settings_gcloud')
django.setup()

def check_connection():
    from django.db import connection
    try:
        with connection.cursor() as c:
            c.execute("SELECT version();")
            print("DB connected:", c.fetchone()[0][:50])
        return True
    except Exception as e:
        print("DB connection failed:", e)
        return False

if __name__ == '__main__':
    print("=== T&TG Database Connection Check ===")
    if check_connection():
        print("Connection OK — ready to migrate")
    else:
        print("Check your DATABASE_URL environment variable")
