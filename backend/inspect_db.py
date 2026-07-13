import sqlite3

def inspect_db(db_path):
    print(f"=== Inspecting {db_path} ===")
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        print("Tables:", [t[0] for t in tables])
        for table in tables:
            t_name = table[0]
            cursor.execute(f"PRAGMA table_info({t_name});")
            info = cursor.fetchall()
            print(f"Table {t_name} schema:")
            for col in info:
                print(f"  {col[1]} ({col[2]})")
            
            # Print first few rows
            cursor.execute(f"SELECT * FROM {t_name} LIMIT 5;")
            rows = cursor.fetchall()
            print(f"Table {t_name} sample rows ({len(rows)}):")
            for r in rows:
                print(f"  {r}")
        conn.close()
    except Exception as e:
        print("Error:", e)

inspect_db("backend/sql_app.db")
inspect_db("sql_app.db")
