"""
CyberGuard AI X - Database Connection Manager
MySQL connection pool using mysql-connector-python
"""

import mysql.connector
from mysql.connector import pooling
from flask import current_app, g
import os


def get_db_config():
    try:
        return {
            'host': current_app.config.get('DB_HOST', 'localhost'),
            'port': int(current_app.config.get('DB_PORT', 3307)),
            'user': current_app.config.get('DB_USER', 'root'),
            'password': current_app.config.get('DB_PASSWORD', ''),
            'database': current_app.config.get('DB_NAME', 'cyberguard_ai'),
            'charset': 'utf8mb4',
            'use_unicode': True,
            'autocommit': False,
        }
    except RuntimeError:
        return {
            'host': os.getenv('DB_HOST', 'localhost'),
            'port': int(os.getenv('DB_PORT', 3307)),
            'user': os.getenv('DB_USER', 'root'),
            'password': os.getenv('DB_PASSWORD', ''),
            'database': os.getenv('DB_NAME', 'cyberguard_ai'),
            'charset': 'utf8mb4',
            'use_unicode': True,
            'autocommit': False,
        }


def get_db():
    """Get database connection (creates one if needed for this request)"""
    if 'db' not in g:
        config = get_db_config()
        g.db = mysql.connector.connect(**config)
    return g.db


def close_db(e=None):
    """Close database connection at end of request"""
    db = g.pop('db', None)
    if db is not None:
        db.close()


def init_db(app):
    """Initialize database, create tables from schema"""
    app.teardown_appcontext(close_db)


def execute_query(query: str, params=None, fetchone=False, fetchall=False, commit=False):
    """
    Execute a database query.
    Returns: results or last insert id
    """
    db = get_db()
    cursor = db.cursor(dictionary=True)
    try:
        cursor.execute(query, params or ())
        if commit:
            db.commit()
            return cursor.lastrowid
        if fetchone:
            return cursor.fetchone()
        if fetchall:
            return cursor.fetchall()
        return None
    except mysql.connector.Error as e:
        db.rollback()
        raise e
    finally:
        cursor.close()


def execute_many(query: str, params_list: list):
    """Execute query for multiple rows"""
    db = get_db()
    cursor = db.cursor()
    try:
        cursor.executemany(query, params_list)
        db.commit()
        return cursor.rowcount
    except mysql.connector.Error as e:
        db.rollback()
        raise e
    finally:
        cursor.close()
