"""
database_generator.py

Generates a complete database with 5 tables, 100 rows each, 5 columns each.
Perfect for SQL practice with realistic data.
"""

import random
import psycopg2
from datetime import datetime, timedelta
from faker import Faker

# Initialize Faker for realistic data generation
fake = Faker()

# Database connection settings
DB_SETTINGS = {
    "dbname": "postgres",
    "user": "postgres",
    "password": "yourpassword",  # Change this to your password
    "host": "localhost",
    "port": "5432"
}

# Number of rows per table
ROWS_PER_TABLE = 100
# Number of columns per table
COLS_PER_TABLE = 5


class DatabaseGenerator:
    """Generates a complete database with realistic data."""
    
    def __init__(self):
        self.conn = None
        self.cursor = None
        
    def connect(self):
        """Connect to PostgreSQL."""
        try:
            self.conn = psycopg2.connect(**DB_SETTINGS)
            self.conn.autocommit = True
            self.cursor = self.conn.cursor()
            print("✅ Connected to PostgreSQL")
            return True
        except Exception as e:
            print(f"❌ Connection failed: {e}")
            return False
    
    def disconnect(self):
        """Close database connection."""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
        print("🔒 Database connection closed")
    
    def drop_tables(self):
        """Drop existing tables if they exist."""
        tables = ['customers', 'products', 'orders', 'order_items', 'payments']
        for table in tables:
            try:
                self.cursor.execute(f"DROP TABLE IF EXISTS {table} CASCADE;")
                print(f"  Dropped table: {table}")
            except Exception as e:
                print(f"  Error dropping {table}: {e}")
    
    def create_tables(self):
        """Create 5 tables with 5 columns each."""
        
        print("\n📊 Creating tables...")
        
        # Table 1: Customers
        self.cursor.execute("""
            CREATE TABLE customers (
                customer_id SERIAL PRIMARY KEY,
                first_name VARCHAR(50) NOT NULL,
                last_name VARCHAR(50) NOT NULL,
                email VARCHAR(100) UNIQUE,
                phone VARCHAR(20),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        print("  ✅ Created: customers")
        
        # Table 2: Products
        self.cursor.execute("""
            CREATE TABLE products (
                product_id SERIAL PRIMARY KEY,
                product_name VARCHAR(100) NOT NULL,
                category VARCHAR(50),
                price DECIMAL(10, 2) NOT NULL,
                stock_quantity INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        print("  ✅ Created: products")
        
        # Table 3: Orders
        self.cursor.execute("""
            CREATE TABLE orders (
                order_id SERIAL PRIMARY KEY,
                customer_id INTEGER REFERENCES customers(customer_id),
                order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status VARCHAR(20) DEFAULT 'PENDING',
                total_amount DECIMAL(10, 2) DEFAULT 0,
                shipping_address TEXT
            );
        """)
        print("  ✅ Created: orders")
        
        # Table 4: Order Items
        self.cursor.execute("""
            CREATE TABLE order_items (
                item_id SERIAL PRIMARY KEY,
                order_id INTEGER REFERENCES orders(order_id),
                product_id INTEGER REFERENCES products(product_id),
                quantity INTEGER DEFAULT 1,
                unit_price DECIMAL(10, 2) NOT NULL,
                discount DECIMAL(5, 2) DEFAULT 0
            );
        """)
        print("  ✅ Created: order_items")
        
        # Table 5: Payments
        self.cursor.execute("""
            CREATE TABLE payments (
                payment_id SERIAL PRIMARY KEY,
                order_id INTEGER REFERENCES orders(order_id),
                payment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                amount DECIMAL(10, 2) NOT NULL,
                payment_method VARCHAR(30),
                status VARCHAR(20) DEFAULT 'PENDING'
            );
        """)
        print("  ✅ Created: payments")
        
        print("\n✅ All 5 tables created successfully!")
    
    def generate_customers(self, count=100):
        """Generate 100 customer records."""
        print(f"\n👤 Generating {count} customers...")
        
        customers = []
        for _ in range(count):
            first_name = fake.first_name()
            last_name = fake.last_name()
            email = f"{first_name.lower()}.{last_name.lower()}{random.randint(1, 999)}@{fake.domain_name()}"
            phone = fake.phone_number()[:20]
            created_at = fake.date_time_between(start_date='-2y', end_date='now')
            
            customers.append((first_name, last_name, email, phone, created_at))
        
        for customer in customers:
            self.cursor.execute("""
                INSERT INTO customers (first_name, last_name, email, phone, created_at)
                VALUES (%s, %s, %s, %s, %s);
            """, customer)
        
        print(f"  ✅ Inserted {count} customers")
        return customers
    
    def generate_products(self, count=100):
        """Generate 100 product records."""
        print(f"\n📦 Generating {count} products...")
        
        categories = ['Electronics', 'Clothing', 'Books', 'Home', 'Sports', 
                     'Toys', 'Food', 'Beauty', 'Health', 'Automotive']
        
        products = []
        for _ in range(count):
            product_name = fake.catch_phrase()[:100]
            category = random.choice(categories)
            price = round(random.uniform(5.99, 999.99), 2)
            stock = random.randint(0, 500)
            created_at = fake.date_time_between(start_date='-1y', end_date='now')
            
            products.append((product_name, category, price, stock, created_at))
        
        for product in products:
            self.cursor.execute("""
                INSERT INTO products (product_name, category, price, stock_quantity, created_at)
                VALUES (%s, %s, %s, %s, %s);
            """, product)
        
        print(f"  ✅ Inserted {count} products")
        return products
    
    def generate_orders(self, count=100):
        """Generate 100 order records."""
        print(f"\n📋 Generating {count} orders...")
        
        # Get customer IDs
        self.cursor.execute("SELECT customer_id FROM customers;")
        customer_ids = [row[0] for row in self.cursor.fetchall()]
        
        statuses = ['PENDING', 'PROCESSING', 'SHIPPED', 'DELIVERED', 'CANCELLED']
        
        orders = []
        for _ in range(count):
            customer_id = random.choice(customer_ids)
            order_date = fake.date_time_between(start_date='-1y', end_date='now')
            status = random.choice(statuses)
            total_amount = round(random.uniform(10.00, 5000.00), 2)
            shipping_address = fake.address().replace('\n', ', ')[:255]
            
            orders.append((customer_id, order_date, status, total_amount, shipping_address))
        
        for order in orders:
            self.cursor.execute("""
                INSERT INTO orders (customer_id, order_date, status, total_amount, shipping_address)
                VALUES (%s, %s, %s, %s, %s);
            """, order)
        
        print(f"  ✅ Inserted {count} orders")
        return orders
    
    def generate_order_items(self, count=100):
        """Generate 100 order item records."""
        print(f"\n🛒 Generating {count} order items...")
        
        # Get order IDs and product IDs
        self.cursor.execute("SELECT order_id FROM orders;")
        order_ids = [row[0] for row in self.cursor.fetchall()]
        
        self.cursor.execute("SELECT product_id, price FROM products;")
        products = [(row[0], row[1]) for row in self.cursor.fetchall()]
        
        order_items = []
        for _ in range(count):
            order_id = random.choice(order_ids)
            product_id, unit_price = random.choice(products)
            quantity = random.randint(1, 10)
            discount = round(random.uniform(0, 0.30), 2)
            
            order_items.append((order_id, product_id, quantity, unit_price, discount))
        
        for item in order_items:
            self.cursor.execute("""
                INSERT INTO order_items (order_id, product_id, quantity, unit_price, discount)
                VALUES (%s, %s, %s, %s, %s);
            """, item)
        
        print(f"  ✅ Inserted {count} order items")
        return order_items
    
    def generate_payments(self, count=100):
        """Generate 100 payment records."""
        print(f"\n💳 Generating {count} payments...")
        
        # Get order IDs
        self.cursor.execute("SELECT order_id FROM orders;")
        order_ids = [row[0] for row in self.cursor.fetchall()]
        
        methods = ['CREDIT_CARD', 'DEBIT_CARD', 'PAYPAL', 'BANK_TRANSFER', 'CASH']
        statuses = ['PENDING', 'COMPLETED', 'FAILED', 'REFUNDED']
        
        payments = []
        for _ in range(count):
            order_id = random.choice(order_ids)
            payment_date = fake.date_time_between(start_date='-1y', end_date='now')
            amount = round(random.uniform(10.00, 5000.00), 2)
            method = random.choice(methods)
            status = random.choice(statuses)
            
            payments.append((order_id, payment_date, amount, method, status))
        
        for payment in payments:
            self.cursor.execute("""
                INSERT INTO payments (order_id, payment_date, amount, payment_method, status)
                VALUES (%s, %s, %s, %s, %s);
            """, payment)
        
        print(f"  ✅ Inserted {count} payments")
        return payments
    
    def generate_all(self):
        """Generate all data."""
        if not self.connect():
            return False
        
        try:
            self.drop_tables()
            self.create_tables()
            
            self.generate_customers(ROWS_PER_TABLE)
            self.generate_products(ROWS_PER_TABLE)
            self.generate_orders(ROWS_PER_TABLE)
            self.generate_order_items(ROWS_PER_TABLE)
            self.generate_payments(ROWS_PER_TABLE)
            
            print("\n" + "=" * 50)
            print("✅ DATABASE GENERATION COMPLETE!")
            print("=" * 50)
            
            # Show summary
            self.show_summary()
            
            return True
            
        except Exception as e:
            print(f"❌ Error generating database: {e}")
            return False
        finally:
            self.disconnect()
    
    def show_summary(self):
        """Show a summary of the generated data."""
        print("\n📊 Database Summary:")
        print("-" * 40)
        
        tables = ['customers', 'products', 'orders', 'order_items', 'payments']
        for table in tables:
            self.cursor.execute(f"SELECT COUNT(*) FROM {table};")
            count = self.cursor.fetchone()[0]
            print(f"  {table}: {count} rows")
        
        print("-" * 40)
        print("\n📝 Sample Queries to Try:")
        print("  SELECT * FROM customers LIMIT 5;")
        print("  SELECT * FROM products WHERE price > 100;")
        print("  SELECT * FROM orders WHERE status = 'DELIVERED';")
        print("  SELECT c.first_name, c.last_name, o.total_amount")
        print("  FROM customers c JOIN orders o ON c.customer_id = o.customer_id;")
        print("  SELECT p.product_name, SUM(oi.quantity) as total_sold")
        print("  FROM products p JOIN order_items oi ON p.product_id = oi.product_id")
        print("  GROUP BY p.product_name ORDER BY total_sold DESC LIMIT 10;")


def main():
    """Main entry point."""
    print("=" * 50)
    print("🗄️  Database Generator")
    print("=" * 50)
    print(f"\n📊 Generating {ROWS_PER_TABLE} rows per table")
    print(f"📋 {5} tables with {5} columns each")
    
    generator = DatabaseGenerator()
    generator.generate_all()


if __name__ == "__main__":
    main()