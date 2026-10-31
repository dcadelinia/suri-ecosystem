import sqlite3
import os 

### Universal cloud-agnostic fallback configuration for isolated microVM environments

DB_DIR = "/data"
if not os.path.exists(DB_DIR):
DB_DIR = "." 

DB_FILE = os.path.join(DB_DIR, "suri_ecosystem.db") 

def init_db():
"""Initializes the database schema for user tiers and remediation metrics tracking."""
conn = sqlite3.connect(DB_FILE)
cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS consumers (
account_id TEXT PRIMARY KEY,
email TEXT NOT NULL,
tier TEXT DEFAULT 'Hobby',
status TEXT DEFAULT 'inactive',
particles_remediated INTEGER DEFAULT 0,
stripe_customer_id TEXT
)
""")
conn.commit()
conn.close() 

def update_consumer_subscription(account_id, email, tier, status, customer_id):
"""Saves or updates active user tier allocations."""
conn = sqlite3.connect(DB_FILE)
cursor = conn.cursor()
cursor.execute("""
INSERT INTO consumers (account_id, email, tier, status, stripe_customer_id)
VALUES (?, ?, ?, ?, ?)
ON CONFLICT(account_id) DO UPDATE SET
tier=excluded.tier,
status=excluded.status,
stripe_customer_id=excluded.stripe_customer_id
""", (account_id, email, tier, status, customer_id))
conn.commit()
conn.close() 

def get_consumer_profile(account_id):
"""Retrieves current customer subscription limits and usage metrics."""
conn = sqlite3.connect(DB_FILE)
cursor = conn.cursor()
cursor.execute("SELECT account_id, email, tier, status, particles_remediated FROM consumers WHERE account_id = ?", (account_id,))
row = cursor.fetchone()
conn.close()
if row:
return {
"account_id": row,
"email": row,
"tier": row,
"status": row,
"particles_remediated": row
}
return None 

init_db()
