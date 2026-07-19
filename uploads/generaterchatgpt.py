import random
from faker import Faker
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

fake = Faker()

# -----------------------------
# PostgreSQL Configuration
# -----------------------------
HOST = "localhost"
PORT = "5432"
USER = "postgres"
PASSWORD = "your_password"
DATABASE = "practice_db"

# -----------------------------
# Create Database
# -----------------------------
try:
    conn = psycopg2.connect(
        host=HOST,
        port=PORT,
        user=USER,
        password=PASSWORD,
        database="postgres"
    )

    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = conn.cursor()

    cur.execute(f"SELECT 1 FROM pg_database WHERE datname='{DATABASE}'")

    if not cur.fetchone():
        cur.execute(f"CREATE DATABASE {DATABASE}")
        print("Database created.")

    cur.close()
    conn.close()

except Exception as e:
    print(e)

# -----------------------------
# Connect to Practice Database
# -----------------------------
conn = psycopg2.connect(
    host=HOST,
    port=PORT,
    user=USER,
    password=PASSWORD,
    database=DATABASE
)

cur = conn.cursor()

# -----------------------------
# Drop Existing Tables
# -----------------------------
cur.execute("""
DROP TABLE IF EXISTS orders;
DROP TABLE IF EXISTS products;
DROP TABLE IF EXISTS customers;
""")

# -----------------------------
# Create Tables
# -----------------------------
cur.execute("""
CREATE TABLE customers(
    customer_id SERIAL PRIMARY KEY,
    customer_name VARCHAR(100),
    city VARCHAR(100)
);
""")

cur.execute("""
CREATE TABLE products(
    product_id SERIAL PRIMARY KEY,
    product_name VARCHAR(100),
    price NUMERIC(10,2)
);
""")

cur.execute("""
CREATE TABLE orders(
    order_id SERIAL PRIMARY KEY,
    customer_id INT REFERENCES customers(customer_id),
    product_id INT REFERENCES products(product_id),
    quantity INT,
    order_date DATE
);
""")

print("Tables created.")

# -----------------------------
# Insert Customers
# -----------------------------
for _ in range(1000):
    cur.execute(
        """
        INSERT INTO customers(customer_name, city)
        VALUES (%s,%s)
        """,
        (
            fake.name(),
            fake.city()
        )
    )

print("Customers inserted.")

# -----------------------------
# Insert Products
# -----------------------------
for _ in range(1000):
    cur.execute(
        """
        INSERT INTO products(product_name, price)
        VALUES (%s,%s)
        """,
        (
            fake.word().capitalize(),
            round(random.uniform(100,5000),2)
        )
    )

print("Products inserted.")

# -----------------------------
# Insert Orders
# -----------------------------
for _ in range(1000):
    cur.execute(
        """
        INSERT INTO orders(customer_id,product_id,quantity,order_date)
        VALUES (%s,%s,%s,%s)
        """,
        (
            random.randint(1,1000),
            random.randint(1,1000),
            random.randint(1,20),
            fake.date_between(start_date='-2y', end_date='today')
        )
    )

print("Orders inserted.")

conn.commit()

cur.close()
conn.close()

print("\nDatabase generation completed successfully!")