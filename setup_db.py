import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE = os.path.join(BASE_DIR, 'spi_database.db')

conn = sqlite3.connect(DATABASE)
cursor = conn.cursor()

cursor.execute("DROP TABLE IF EXISTS applications")

cursor.execute('''
    CREATE TABLE applications (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        full_name TEXT NOT NULL,
        gender TEXT NOT NULL,
        dob TEXT NOT NULL,
        phone TEXT NOT NULL,
        email TEXT NOT NULL,
        address TEXT NOT NULL,
        province TEXT NOT NULL,
        program TEXT NOT NULL,
        high_school TEXT NOT NULL,
        grade TEXT NOT NULL,
        scholarship TEXT DEFAULT 'no',
        notes TEXT,
        status TEXT DEFAULT 'pending',
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
''')

conn.commit()
print(f"SUCCESS: Database = {DATABASE}")
print("Applications table created")
conn.close()