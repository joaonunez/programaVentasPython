# db.py
import mysql.connector
from config import db_config

conn = mysql.connector.connect(**db_config)
cursor = conn.cursor()

def execute_query(query, params=None):
    try:
        cursor.execute(query, params)
        conn.commit()
    except mysql.connector.Error as err:
        print(f"Error: {err}")

def fetch_all(query, params=None):
    try:
        cursor.execute(query, params)
        return cursor.fetchall()
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return []

def fetch_one(query, params=None):
    try:
        cursor.execute(query, params)
        return cursor.fetchone()
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None
