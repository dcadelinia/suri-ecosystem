import os
import sqlite3

DATA_DIR = os.getenv("DATA_DIR", "/data")
os.makedirs(DATA_DIR, exist_ok=True)
DB_FILE = os.path.join(DATA_DIR, "suri_ecosystem.db")

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS consumers (
            account_id TEXT PRIMARY KEY,
            email TEXT NOT NULL,
            tier TEXT DEFAULT 'Hobby',
            status TEXT DEFAULT 'inactive'
        )
    """)
    conn.commit()
    conn.close()
