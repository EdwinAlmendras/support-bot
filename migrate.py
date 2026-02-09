import sqlite3
import os

db_path = "/app/data/bot.db"
if not os.path.exists(db_path):
    # Try local path for testing
    db_path = "data/bot.db"

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

try:
    print("Checking broadcast_queue schema...")
    cursor.execute("PRAGMA table_info(broadcast_queue)")
    columns = [col[1] for col in cursor.fetchall()]
    
    if "chat_id" not in columns:
        print("Adding 'chat_id' column to 'broadcast_queue'...")
        # BigInteger maps to INTEGER in SQLite
        cursor.execute("ALTER TABLE broadcast_queue ADD COLUMN chat_id BIGINT")
        conn.commit()
        print("Column added successfully.")
    else:
        print("'chat_id' column already exists.")

    # Also ensure indexes if applicable, but let's stick to the basics first
except Exception as e:
    print(f"Error during migration: {e}")
finally:
    conn.close()
