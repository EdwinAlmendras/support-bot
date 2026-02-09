import sqlite3
import os

db_path = "/app/data/bot.db"
if not os.path.exists(db_path):
    db_path = "data/bot.db"

def fix_schema():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        cursor.execute("PRAGMA table_info(bot_settings)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if "chat_id" not in columns:
            print("Detected old bot_settings schema (missing chat_id). Dropping table...")
            cursor.execute("DROP TABLE bot_settings")
            conn.commit()
            print("Table dropped. Restart the bot to recreate it with the new schema.")
        else:
            print("bot_settings schema looks correct.")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    fix_schema()
