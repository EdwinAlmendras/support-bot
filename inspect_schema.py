import sqlite3
import os

DB_PATH = "data/bot.db"

def inspect_schema():
    if not os.path.exists(DB_PATH):
        print("DB does not exist")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        cursor.execute("PRAGMA table_info(bot_settings);")
        columns = cursor.fetchall()
        print("Schema for bot_settings:")
        for col in columns:
            print(col)
            
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        print("\nTables:", tables)

    except Exception as e:
        print(e)
    finally:
        conn.close()

if __name__ == "__main__":
    inspect_schema()
