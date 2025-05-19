import sqlite3
from datetime import datetime

class DatabaseManager:
    def __init__(self, dbName=None):
        self.cx = sqlite3.connect(dbName or "products.db")
        self.cu = self.cx.cursor()
        self._create_tables()

    def _create_tables(self):
        self.cu.execute("""
            CREATE TABLE IF NOT EXISTS selection (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                product_count INTEGER NOT NULL
            );
        """)
        self.cu.execute("""
            CREATE TABLE IF NOT EXISTS products (
                selection_id INTEGER,
                name TEXT,
                price TEXT,
                FOREIGN KEY (selection_id) REFERENCES selection(id)
            );
        """)
        self.cx.commit()

    def insert_parsing_results(self, products):
        date = datetime.now().strftime("%d.%m.%Y %H:%M:%S")
        product_count = len(products)

        self.cu.execute("INSERT INTO selection (date, product_count) VALUES (?, ?)", (date, product_count))
        selection_id = self.cu.lastrowid

        self.cu.executemany(
            "INSERT INTO products (selection_id, name, price) VALUES (?, ?, ?)",
            [(selection_id, name, price) for name, price in products]
        )

        self.cx.commit()

    def get_selections(self):
        self.cu.execute("SELECT * FROM selection")
        return self.cu.fetchall()

    def get_products_by_selecID(self, selection_id):
        self.cu.execute("SELECT * FROM products WHERE selection_id = ?", (selection_id,))
        return self.cu.fetchall()
    
    def search_products(self, query):
        pattern = f"%{query.lower()}%"
        self.cu.execute("""
            SELECT selection_id, name, price
            FROM products
            WHERE LOWER(name) LIKE ? OR LOWER(price) LIKE ?
        """, (pattern, pattern))
        return self.cu.fetchall()

    def close(self):
        self.cx.close()
