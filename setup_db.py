import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE = os.path.join(BASE_DIR, 'spi_database_from_ubuntu.db')

print(f"📁 Database: {DATABASE}")

conn = sqlite3.connect(DATABASE)
cursor = conn.cursor()

# បង្កើត Table តែប្រសិនបើមិនទាន់មាន (មិនលុបទិន្នន័យចាស់)
cursor.execute('''
    CREATE TABLE IF NOT EXISTS applications (
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

cursor.execute("SELECT COUNT(*) FROM applications")
count = cursor.fetchone()[0]

print(f"✅ Database ready!")
print(f"📊 ចំនួនទិន្នន័យ: {count} rows")

conn.close()