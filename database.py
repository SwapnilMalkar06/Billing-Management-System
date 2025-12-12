import mysql.connector
import hashlib
import pandas as pd
from datetime import datetime

class ShopDatabase:
    def __init__(self):
        # Configuration for MySQL connection
        self.host = "localhost"
        self.user = "root"
        self.password = "852456"
        self.database = "shop_inventory"
        
        self.conn = None
        self.cursor = None
        
        self.init_database()
        self.connect()
        self.create_tables()
        self.seed_default_user()

    def init_database(self):
        """Connect to server and create database if it doesn't exist"""
        try:
            temp_conn = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password
            )
            temp_cursor = temp_conn.cursor()
            temp_cursor.execute(f"CREATE DATABASE IF NOT EXISTS {self.database}")
            temp_conn.close()
        except mysql.connector.Error as err:
            print(f"Error initializing database: {err}")

    def connect(self):
        """Connect to the specific database"""
        try:
            self.conn = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database
            )
            # FIX: buffered=True prevents 'Unread result found' errors
            # when previous queries don't consume all rows.
            self.cursor = self.conn.cursor(buffered=True)
        except mysql.connector.Error as err:
            print(f"Error connecting: {err}")

    def create_tables(self):
        # Users Table (Using VARCHAR for Unique keys in MySQL)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(255) UNIQUE NOT NULL,
                password VARCHAR(255) NOT NULL,
                role VARCHAR(50) NOT NULL
            )
        """)
        
        # Products Table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS products (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                category VARCHAR(100) NOT NULL,
                price DECIMAL(10, 2) NOT NULL,
                stock INT NOT NULL,
                min_stock INT DEFAULT 10
            )
        """)
        
        # Sales Table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS sales (
                invoice_id VARCHAR(255) PRIMARY KEY,
                date DATETIME NOT NULL,
                subtotal DECIMAL(10, 2) NOT NULL,
                tax DECIMAL(10, 2) NOT NULL,
                discount DECIMAL(10, 2) NOT NULL,
                grand_total DECIMAL(10, 2) NOT NULL
            )
        """)
        
        # Sale Items Table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS sale_items (
                id INT AUTO_INCREMENT PRIMARY KEY,
                invoice_id VARCHAR(255),
                product_id INT,
                product_name VARCHAR(255),
                quantity INT,
                price DECIMAL(10, 2),
                total DECIMAL(10, 2),
                FOREIGN KEY(invoice_id) REFERENCES sales(invoice_id)
            )
        """)
        self.conn.commit()

    def seed_default_user(self):
        # Create a default admin if no users exist
        # FIX: Use LIMIT 1 to ensure we don't leave unread rows if multiple users exist
        self.cursor.execute("SELECT * FROM users LIMIT 1")
        if not self.cursor.fetchone():
            self.add_user("admin", "admin123", "Admin")

    def hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()

    def add_user(self, username, password, role):
        try:
            hashed_pw = self.hash_password(password)
            # MySQL uses %s as placeholder
            self.cursor.execute("INSERT INTO users (username, password, role) VALUES (%s, %s, %s)",
                                (username, hashed_pw, role))
            self.conn.commit()
            return True
        except mysql.connector.IntegrityError:
            return False

    def verify_login(self, username, password):
        hashed_pw = self.hash_password(password)
        self.cursor.execute("SELECT role FROM users WHERE username=%s AND password=%s", (username, hashed_pw))
        result = self.cursor.fetchone()
        return result[0] if result else None

    # --- Inventory Operations ---
    def add_product(self, name, category, price, stock, min_stock):
        sql = "INSERT INTO products (name, category, price, stock, min_stock) VALUES (%s, %s, %s, %s, %s)"
        val = (name, category, price, stock, min_stock)
        self.cursor.execute(sql, val)
        self.conn.commit()

    def update_product(self, pid, name, category, price, stock, min_stock):
        sql = """
            UPDATE products SET name=%s, category=%s, price=%s, stock=%s, min_stock=%s WHERE id=%s
        """
        val = (name, category, price, stock, min_stock, pid)
        self.cursor.execute(sql, val)
        self.conn.commit()

    def delete_product(self, pid):
        self.cursor.execute("DELETE FROM products WHERE id=%s", (pid,))
        self.conn.commit()

    def get_all_products(self):
        self.cursor.execute("SELECT * FROM products")
        return self.cursor.fetchall()
    
    def search_products(self, query):
        # Search by ID or Name
        search_term = f"%{query}%"
        self.cursor.execute("SELECT * FROM products WHERE name LIKE %s OR id LIKE %s", (search_term, search_term))
        return self.cursor.fetchall()

    def get_product_by_id(self, pid):
        self.cursor.execute("SELECT * FROM products WHERE id=%s", (pid,))
        return self.cursor.fetchone()

    # --- Billing Operations ---
    def process_sale(self, invoice_id, customer_data, cart_items, financials):
        try:
            date_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Insert Sale Record
            self.cursor.execute("""
                INSERT INTO sales (invoice_id, date, subtotal, tax, discount, grand_total)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (invoice_id, date_str, financials['subtotal'], financials['tax'], financials['discount'], financials['grand_total']))

            # Insert Sale Items and Update Stock
            for item in cart_items:
                # item: [pid, name, price, qty, total]
                pid, name, price, qty, total = item
                
                self.cursor.execute("""
                    INSERT INTO sale_items (invoice_id, product_id, product_name, quantity, price, total)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (invoice_id, pid, name, qty, price, total))

                # Deduct Stock
                self.cursor.execute("UPDATE products SET stock = stock - %s WHERE id = %s", (qty, pid))
            
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error processing sale: {e}")
            self.conn.rollback()
            return False

    # --- Reporting Operations (Pandas) ---
    def get_sales_data(self):
        # Pandas read_sql works with mysql connector connections
        return pd.read_sql("SELECT * FROM sales", self.conn)

    def get_item_sales_data(self):
        return pd.read_sql("SELECT * FROM sale_items", self.conn)

    def get_inventory_data(self):
        return pd.read_sql("SELECT * FROM products", self.conn)
    
    def close(self):
        if self.conn:
            self.conn.close()