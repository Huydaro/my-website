import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE = os.path.join(BASE_DIR, 'my_test_database.db')

conn = sqlite3.connect(DATABASE)
cursor = conn.cursor()

# លុប Table ចាស់
cursor.execute("DROP TABLE IF EXISTS users")
cursor.execute("DROP TABLE IF EXISTS bookings")
cursor.execute("DROP TABLE IF EXISTS services")
cursor.execute("DROP TABLE IF EXISTS orders")
cursor.execute("DROP TABLE IF EXISTS products")

# បង្កើត Table products
cursor.execute('''
    CREATE TABLE products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        model TEXT NOT NULL,
        storage TEXT NOT NULL,
        color TEXT,
        price REAL NOT NULL DEFAULT 0,
        stock INTEGER DEFAULT 0,
        image TEXT,
        description TEXT,
        year INTEGER,
        featured INTEGER DEFAULT 0,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
''')

# បង្កើត Table orders
cursor.execute('''
    CREATE TABLE orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        product_id INTEGER NOT NULL,
        customer_name TEXT NOT NULL,
        customer_email TEXT NOT NULL,
        customer_phone TEXT,
        address TEXT,
        quantity INTEGER DEFAULT 1,
        total_price REAL,
        status TEXT DEFAULT 'pending',
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (product_id) REFERENCES products(id)
    )
''')

# បញ្ចូល iPhone គំរូ
iphones = [
    ('iPhone 5', '16GB', 'Black', 99.00, 50, 2012, 0, 'iPhone 5 - Lightning Port និងអេក្រង់ 4 អ៊ីញ'),
    ('iPhone 6', '32GB', 'Space Gray', 129.00, 40, 2014, 0, 'iPhone 6 - អេក្រង់ធំ 4.7 អ៊ីញ'),
    ('iPhone 7', '64GB', 'Jet Black', 179.00, 35, 2016, 0, 'iPhone 7 - គ្មាន Jack កាសស្តាប់'),
    ('iPhone 8', '64GB', 'Gold', 229.00, 30, 2017, 0, 'iPhone 8 - Wireless Charging'),
    ('iPhone X', '64GB', 'Silver', 299.00, 25, 2017, 0, 'iPhone X - Face ID និង Full Screen'),
    ('iPhone XR', '128GB', 'Blue', 349.00, 30, 2018, 0, 'iPhone XR - ពណ៌ច្រើន'),
    ('iPhone 11', '128GB', 'Purple', 399.00, 40, 2019, 1, 'iPhone 11 - កាមេរ៉ាពីរ Night Mode'),
    ('iPhone 12', '128GB', 'Blue', 499.00, 45, 2020, 1, 'iPhone 12 - 5G និង MagSafe'),
    ('iPhone 13', '128GB', 'Pink', 599.00, 50, 2021, 1, 'iPhone 13 - Cinematic Mode'),
    ('iPhone 14', '128GB', 'Purple', 699.00, 40, 2022, 1, 'iPhone 14 - Crash Detection'),
    ('iPhone 15', '256GB', 'Black', 899.00, 35, 2023, 1, 'iPhone 15 - USB-C និង Dynamic Island'),
    ('iPhone 16', '256GB', 'Natural', 999.00, 30, 2024, 1, 'iPhone 16 - A18 Chip Camera Control'),
    ('iPhone 17', '256GB', 'Teal', 1099.00, 25, 2025, 1, 'iPhone 17 - A19 Chip Apple Intelligence'),
    ('iPhone 18', '256GB', 'Black', 1199.00, 20, 2026, 1, 'iPhone 18 - A20 Chip 48MP'),
    ('iPhone 18 Pro', '512GB', 'Titanium', 1499.00, 15, 2026, 1, 'iPhone 18 Pro - Titanium ProMotion'),
    ('iPhone 18 Pro Max', '1TB', 'Desert Titanium', 1799.00, 10, 2026, 1, 'iPhone 18 Pro Max - កំពូលបំផុត'),
]

for model, storage, color, price, stock, year, featured, desc in iphones:
    cursor.execute(
        """INSERT INTO products (model, storage, color, price, stock, year, featured, description, image) 
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (model, storage, color, price, stock, year, featured, desc, '')
    )

conn.commit()

cursor.execute("SELECT COUNT(*) FROM products")
print(f"SUCCESS: Database = {DATABASE}")
print(f"iPhone Models: {cursor.fetchone()[0]}")
print(f"Orders: 0")

conn.close()