"""
CyberGuard AI X - Seed Admin User
Run: python backend/seed_admin.py
Creates default admin account in the database.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import bcrypt
import mysql.connector
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', ''),
    'database': os.getenv('DB_NAME', 'cyberguard_ai'),
    'charset': 'utf8mb4',
}

ADMIN_EMAIL = 'admin@cyberguard.ai'
ADMIN_PASSWORD = 'Admin@123'
ADMIN_NAME = 'CyberGuard Admin'

def seed_admin():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor(dictionary=True)

        # Check if admin exists
        cursor.execute("SELECT id FROM users WHERE email = %s", (ADMIN_EMAIL,))
        existing = cursor.fetchone()
        if existing:
            print(f"Admin already exists: {ADMIN_EMAIL}")
            return

        # Hash password
        hashed = bcrypt.hashpw(ADMIN_PASSWORD.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        # Insert admin
        cursor.execute(
            "INSERT INTO users (name, email, password, role) VALUES (%s, %s, %s, 'admin')",
            (ADMIN_NAME, ADMIN_EMAIL, hashed)
        )
        conn.commit()
        print(f"✅ Admin created successfully!")
        print(f"   Email:    {ADMIN_EMAIL}")
        print(f"   Password: {ADMIN_PASSWORD}")
        print(f"   Role:     admin")

        cursor.close()
        conn.close()

    except mysql.connector.Error as e:
        print(f"❌ Database error: {e}")
        print("   Make sure XAMPP MySQL is running and the database exists.")
        print("   Run: database/schema.sql first.")

if __name__ == '__main__':
    seed_admin()
