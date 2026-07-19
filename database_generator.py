#!/usr/bin/env python3
"""
database_generator.py - Generates realistic databases for different business domains
"""

import random
import psycopg2
import argparse
from datetime import datetime, timedelta
from faker import Faker

fake = Faker()

DB_SETTINGS = {
    "dbname": "postgres",
    "user": "postgres",
    "password": "4m4teur",
    "host": "localhost",
    "port": "5432"
}

DOMAINS = {
    'ecommerce': {
        'name': '🛒 E-Commerce',
        'tables': {
            'customers': {
                'columns': [
                    {'name': 'customer_id', 'type': 'SERIAL PRIMARY KEY'},
                    {'name': 'first_name', 'type': 'VARCHAR(50) NOT NULL'},
                    {'name': 'last_name', 'type': 'VARCHAR(50) NOT NULL'},
                    {'name': 'email', 'type': 'VARCHAR(100) UNIQUE'},
                    {'name': 'phone', 'type': 'VARCHAR(20)'},
                    {'name': 'created_at', 'type': 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP'}
                ],
                'generator': 'generate_customers'
            },
            'products': {
                'columns': [
                    {'name': 'product_id', 'type': 'SERIAL PRIMARY KEY'},
                    {'name': 'product_name', 'type': 'VARCHAR(150) NOT NULL'},
                    {'name': 'category', 'type': 'VARCHAR(50)'},
                    {'name': 'price', 'type': 'DECIMAL(10,2) NOT NULL'},
                    {'name': 'stock_quantity', 'type': 'INTEGER DEFAULT 0'},
                    {'name': 'created_at', 'type': 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP'}
                ],
                'generator': 'generate_products'
            },
            'orders': {
                'columns': [
                    {'name': 'order_id', 'type': 'SERIAL PRIMARY KEY'},
                    {'name': 'customer_id', 'type': 'INTEGER REFERENCES customers(customer_id)'},
                    {'name': 'order_date', 'type': 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP'},
                    {'name': 'status', 'type': 'VARCHAR(20) DEFAULT \'PENDING\''},
                    {'name': 'total_amount', 'type': 'DECIMAL(10,2) DEFAULT 0'}
                ],
                'generator': 'generate_orders'
            },
            'order_items': {
                'columns': [
                    {'name': 'item_id', 'type': 'SERIAL PRIMARY KEY'},
                    {'name': 'order_id', 'type': 'INTEGER REFERENCES orders(order_id)'},
                    {'name': 'product_id', 'type': 'INTEGER REFERENCES products(product_id)'},
                    {'name': 'quantity', 'type': 'INTEGER DEFAULT 1'},
                    {'name': 'unit_price', 'type': 'DECIMAL(10,2) NOT NULL'}
                ],
                'generator': 'generate_order_items'
            },
            'payments': {
                'columns': [
                    {'name': 'payment_id', 'type': 'SERIAL PRIMARY KEY'},
                    {'name': 'order_id', 'type': 'INTEGER REFERENCES orders(order_id)'},
                    {'name': 'payment_date', 'type': 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP'},
                    {'name': 'amount', 'type': 'DECIMAL(10,2) NOT NULL'},
                    {'name': 'status', 'type': 'VARCHAR(20) DEFAULT \'PENDING\''}
                ],
                'generator': 'generate_payments'
            }
        }
    },
    'hr': {
        'name': '👥 Human Resources',
        'tables': {
            'employees': {
                'columns': [
                    {'name': 'employee_id', 'type': 'SERIAL PRIMARY KEY'},
                    {'name': 'first_name', 'type': 'VARCHAR(50) NOT NULL'},
                    {'name': 'last_name', 'type': 'VARCHAR(50) NOT NULL'},
                    {'name': 'email', 'type': 'VARCHAR(100) UNIQUE'},
                    {'name': 'hire_date', 'type': 'DATE'},
                    {'name': 'department', 'type': 'VARCHAR(50)'},
                    {'name': 'salary', 'type': 'DECIMAL(10,2)'}
                ],
                'generator': 'generate_employees'
            },
            'departments': {
                'columns': [
                    {'name': 'department_id', 'type': 'SERIAL PRIMARY KEY'},
                    {'name': 'department_name', 'type': 'VARCHAR(50) NOT NULL'},
                    {'name': 'budget', 'type': 'DECIMAL(12,2)'}
                ],
                'generator': 'generate_departments'
            }
        }
    },
    'healthcare': {
        'name': '🏥 Healthcare',
        'tables': {
            'patients': {
                'columns': [
                    {'name': 'patient_id', 'type': 'SERIAL PRIMARY KEY'},
                    {'name': 'first_name', 'type': 'VARCHAR(50) NOT NULL'},
                    {'name': 'last_name', 'type': 'VARCHAR(50) NOT NULL'},
                    {'name': 'date_of_birth', 'type': 'DATE'},
                    {'name': 'gender', 'type': 'VARCHAR(10)'},
                    {'name': 'blood_type', 'type': 'VARCHAR(5)'}
                ],
                'generator': 'generate_patients'
            },
            'doctors': {
                'columns': [
                    {'name': 'doctor_id', 'type': 'SERIAL PRIMARY KEY'},
                    {'name': 'first_name', 'type': 'VARCHAR(50) NOT NULL'},
                    {'name': 'last_name', 'type': 'VARCHAR(50) NOT NULL'},
                    {'name': 'specialty', 'type': 'VARCHAR(50)'},
                    {'name': 'phone', 'type': 'VARCHAR(20)'}
                ],
                'generator': 'generate_doctors'
            },
            'appointments': {
                'columns': [
                    {'name': 'appointment_id', 'type': 'SERIAL PRIMARY KEY'},
                    {'name': 'patient_id', 'type': 'INTEGER REFERENCES patients(patient_id)'},
                    {'name': 'doctor_id', 'type': 'INTEGER REFERENCES doctors(doctor_id)'},
                    {'name': 'appointment_date', 'type': 'TIMESTAMP'},
                    {'name': 'status', 'type': 'VARCHAR(20) DEFAULT \'SCHEDULED\''}
                ],
                'generator': 'generate_appointments'
            }
        }
    },
    'finance': {
        'name': '💰 Finance & Banking',
        'tables': {
            'accounts': {
                'columns': [
                    {'name': 'account_id', 'type': 'SERIAL PRIMARY KEY'},
                    {'name': 'account_number', 'type': 'VARCHAR(20) UNIQUE'},
                    {'name': 'customer_name', 'type': 'VARCHAR(100) NOT NULL'},
                    {'name': 'account_type', 'type': 'VARCHAR(20)'},
                    {'name': 'balance', 'type': 'DECIMAL(12,2) DEFAULT 0'}
                ],
                'generator': 'generate_accounts'
            },
            'transactions': {
                'columns': [
                    {'name': 'transaction_id', 'type': 'SERIAL PRIMARY KEY'},
                    {'name': 'account_id', 'type': 'INTEGER REFERENCES accounts(account_id)'},
                    {'name': 'transaction_date', 'type': 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP'},
                    {'name': 'amount', 'type': 'DECIMAL(12,2) NOT NULL'},
                    {'name': 'transaction_type', 'type': 'VARCHAR(20)'}
                ],
                'generator': 'generate_transactions'
            },
            'loans': {
                'columns': [
                    {'name': 'loan_id', 'type': 'SERIAL PRIMARY KEY'},
                    {'name': 'account_id', 'type': 'INTEGER REFERENCES accounts(account_id)'},
                    {'name': 'loan_amount', 'type': 'DECIMAL(12,2) NOT NULL'},
                    {'name': 'interest_rate', 'type': 'DECIMAL(5,2)'},
                    {'name': 'status', 'type': 'VARCHAR(20) DEFAULT \'ACTIVE\''}
                ],
                'generator': 'generate_loans'
            }
        }
    },
    'education': {
        'name': '🎓 Education',
        'tables': {
            'students': {
                'columns': [
                    {'name': 'student_id', 'type': 'SERIAL PRIMARY KEY'},
                    {'name': 'first_name', 'type': 'VARCHAR(50) NOT NULL'},
                    {'name': 'last_name', 'type': 'VARCHAR(50) NOT NULL'},
                    {'name': 'email', 'type': 'VARCHAR(100) UNIQUE'},
                    {'name': 'major', 'type': 'VARCHAR(50)'},
                    {'name': 'gpa', 'type': 'DECIMAL(3,2)'}
                ],
                'generator': 'generate_students'
            },
            'courses': {
                'columns': [
                    {'name': 'course_id', 'type': 'SERIAL PRIMARY KEY'},
                    {'name': 'course_code', 'type': 'VARCHAR(10) UNIQUE'},
                    {'name': 'course_name', 'type': 'VARCHAR(100) NOT NULL'},
                    {'name': 'credits', 'type': 'INTEGER'},
                    {'name': 'instructor', 'type': 'VARCHAR(100)'}
                ],
                'generator': 'generate_courses'
            },
            'enrollments': {
                'columns': [
                    {'name': 'enrollment_id', 'type': 'SERIAL PRIMARY KEY'},
                    {'name': 'student_id', 'type': 'INTEGER REFERENCES students(student_id)'},
                    {'name': 'course_id', 'type': 'INTEGER REFERENCES courses(course_id)'},
                    {'name': 'grade', 'type': 'VARCHAR(2)'},
                    {'name': 'status', 'type': 'VARCHAR(20) DEFAULT \'ENROLLED\''}
                ],
                'generator': 'generate_enrollments'
            }
        }
    }
}

class DatabaseGenerator:
    def __init__(self, domain='ecommerce', rows=100):
        self.domain = domain
        self.rows = rows
        self.conn = None
        self.cursor = None
        
    def connect(self):
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
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
        print("🔒 Database connection closed")
    
    def drop_all_tables(self):
        """Drop ALL tables in the public schema."""
        self.cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema='public'
        """)
        tables = [row[0] for row in self.cursor.fetchall()]
        if not tables:
            return
        print(f"🗑️  Dropping {len(tables)} existing tables...")
        for table in tables:
            self.cursor.execute(f"DROP TABLE IF EXISTS {table} CASCADE;")
            print(f"  Dropped: {table}")
    
    def create_tables(self):
        domain_data = DOMAINS.get(self.domain, DOMAINS['ecommerce'])
        print(f"\n📊 Creating tables for {domain_data['name']}...")
        for table_name, table_info in domain_data['tables'].items():
            columns_sql = ", ".join([f"{col['name']} {col['type']}" for col in table_info['columns']])
            self.cursor.execute(f"CREATE TABLE IF NOT EXISTS {table_name} ({columns_sql});")
            print(f"  ✅ Created: {table_name}")
        print("\n✅ All tables created successfully!")
    
    def generate_data(self):
        domain_data = DOMAINS.get(self.domain, DOMAINS['ecommerce'])
        print(f"\n📊 Generating {self.rows} rows per table...")
        for table_name, table_info in domain_data['tables'].items():
            generator_method = getattr(self, table_info['generator'], None)
            if generator_method:
                generator_method(self.rows)
            else:
                print(f"  ⚠️ No generator for {table_name}")
    
    # ECOMMERCE GENERATORS
    def generate_customers(self, count):
        print(f"\n👤 Generating {count} customers...")
        for _ in range(count):
            first_name = fake.first_name()
            last_name = fake.last_name()
            email = f"{first_name.lower()}.{last_name.lower()}{random.randint(1,999)}@{fake.domain_name()}"
            phone = fake.phone_number()[:20]
            created_at = fake.date_time_between(start_date='-2y', end_date='now')
            self.cursor.execute("""INSERT INTO customers (first_name, last_name, email, phone, created_at) VALUES (%s,%s,%s,%s,%s);""", (first_name, last_name, email, phone, created_at))
        print(f"  ✅ Inserted {count} customers")
    
    def generate_products(self, count):
        print(f"\n📦 Generating {count} products...")
        categories = ['Electronics', 'Clothing', 'Books', 'Home', 'Sports', 'Toys']
        for _ in range(count):
            category = random.choice(categories)
            product_name = fake.catch_phrase()[:100]
            price = round(random.uniform(5.99, 999.99), 2)
            stock = random.randint(0, 500)
            created_at = fake.date_time_between(start_date='-1y', end_date='now')
            self.cursor.execute("""INSERT INTO products (product_name, category, price, stock_quantity, created_at) VALUES (%s,%s,%s,%s,%s);""", (product_name, category, price, stock, created_at))
        print(f"  ✅ Inserted {count} products")
    
    def generate_orders(self, count):
        print(f"\n📋 Generating {count} orders...")
        self.cursor.execute("SELECT customer_id FROM customers;")
        customer_ids = [row[0] for row in self.cursor.fetchall()]
        if not customer_ids: print("  ⚠️ No customers found!"); return
        statuses = ['PENDING', 'PROCESSING', 'SHIPPED', 'DELIVERED', 'CANCELLED']
        for _ in range(count):
            customer_id = random.choice(customer_ids)
            order_date = fake.date_time_between(start_date='-1y', end_date='now')
            status = random.choice(statuses)
            total_amount = round(random.uniform(10.00, 5000.00), 2)
            self.cursor.execute("""INSERT INTO orders (customer_id, order_date, status, total_amount) VALUES (%s,%s,%s,%s);""", (customer_id, order_date, status, total_amount))
        print(f"  ✅ Inserted {count} orders")
    
    def generate_order_items(self, count):
        print(f"\n🛒 Generating {count} order items...")
        self.cursor.execute("SELECT order_id FROM orders;")
        order_ids = [row[0] for row in self.cursor.fetchall()]
        self.cursor.execute("SELECT product_id, price FROM products;")
        products = [(row[0], row[1]) for row in self.cursor.fetchall()]
        if not order_ids or not products: print("  ⚠️ No orders or products found!"); return
        for _ in range(count):
            order_id = random.choice(order_ids)
            product_id, unit_price = random.choice(products)
            quantity = random.randint(1, 10)
            self.cursor.execute("""INSERT INTO order_items (order_id, product_id, quantity, unit_price) VALUES (%s,%s,%s,%s);""", (order_id, product_id, quantity, unit_price))
        print(f"  ✅ Inserted {count} order_items")
    
    def generate_payments(self, count):
        print(f"\n💳 Generating {count} payments...")
        self.cursor.execute("SELECT order_id FROM orders;")
        order_ids = [row[0] for row in self.cursor.fetchall()]
        if not order_ids: print("  ⚠️ No orders found!"); return
        methods = ['Credit Card', 'Debit Card', 'PayPal', 'Bank Transfer']
        statuses = ['PENDING', 'COMPLETED', 'FAILED', 'REFUNDED']
        for _ in range(count):
            order_id = random.choice(order_ids)
            payment_date = fake.date_time_between(start_date='-1y', end_date='now')
            amount = round(random.uniform(10.00, 5000.00), 2)
            method = random.choice(methods)
            status = random.choice(statuses)
            self.cursor.execute("""INSERT INTO payments (order_id, payment_date, amount, payment_method, status) VALUES (%s,%s,%s,%s,%s);""", (order_id, payment_date, amount, method, status))
        print(f"  ✅ Inserted {count} payments")
    
    # HR GENERATORS
    def generate_employees(self, count):
        print(f"\n👔 Generating {count} employees...")
        departments = ['Engineering', 'Sales', 'Marketing', 'HR', 'Finance', 'Operations']
        for _ in range(count):
            first_name = fake.first_name()
            last_name = fake.last_name()
            email = f"{first_name.lower()}.{last_name.lower()}@{fake.domain_name()}"
            hire_date = fake.date_between(start_date='-10y', end_date='today')
            department = random.choice(departments)
            salary = round(random.uniform(40000, 150000), 2)
            self.cursor.execute("""INSERT INTO employees (first_name, last_name, email, hire_date, department, salary) VALUES (%s,%s,%s,%s,%s,%s);""", (first_name, last_name, email, hire_date, department, salary))
        print(f"  ✅ Inserted {count} employees")
    
    def generate_departments(self, count):
        print(f"\n🏢 Generating {count} departments...")
        dept_names = ['Engineering', 'Sales', 'Marketing', 'HR', 'Finance', 'Operations', 'IT', 'Legal']
        for i in range(min(count, len(dept_names))):
            dept_name = dept_names[i % len(dept_names)]
            budget = round(random.uniform(50000, 1000000), 2)
            self.cursor.execute("""INSERT INTO departments (department_name, budget) VALUES (%s,%s);""", (dept_name, budget))
        print(f"  ✅ Inserted {min(count, len(dept_names))} departments")
    
    # HEALTHCARE GENERATORS
    def generate_patients(self, count):
        print(f"\n🏥 Generating {count} patients...")
        genders = ['M', 'F', 'Other']
        blood_types = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']
        for _ in range(count):
            first_name = fake.first_name()
            last_name = fake.last_name()
            dob = fake.date_between(start_date='-80y', end_date='-1y')
            gender = random.choice(genders)
            blood_type = random.choice(blood_types)
            self.cursor.execute("""INSERT INTO patients (first_name, last_name, date_of_birth, gender, blood_type) VALUES (%s,%s,%s,%s,%s);""", (first_name, last_name, dob, gender, blood_type))
        print(f"  ✅ Inserted {count} patients")
    
    def generate_doctors(self, count):
        print(f"\n👨‍⚕️ Generating {count} doctors...")
        specialties = ['Cardiology', 'Dermatology', 'Neurology', 'Pediatrics', 'Oncology', 'Orthopedics', 'Psychiatry', 'Radiology']
        for _ in range(count):
            first_name = fake.first_name()
            last_name = fake.last_name()
            specialty = random.choice(specialties)
            phone = fake.phone_number()[:20]
            self.cursor.execute("""INSERT INTO doctors (first_name, last_name, specialty, phone) VALUES (%s,%s,%s,%s);""", (first_name, last_name, specialty, phone))
        print(f"  ✅ Inserted {count} doctors")
    
    def generate_appointments(self, count):
        print(f"\n📅 Generating {count} appointments...")
        self.cursor.execute("SELECT patient_id FROM patients;")
        patient_ids = [row[0] for row in self.cursor.fetchall()]
        self.cursor.execute("SELECT doctor_id FROM doctors;")
        doctor_ids = [row[0] for row in self.cursor.fetchall()]
        statuses = ['SCHEDULED', 'COMPLETED', 'CANCELLED', 'NO_SHOW']
        for _ in range(count):
            patient_id = random.choice(patient_ids) if patient_ids else None
            doctor_id = random.choice(doctor_ids) if doctor_ids else None
            appointment_date = fake.date_time_between(start_date='-6m', end_date='+6m')
            status = random.choice(statuses)
            self.cursor.execute("""INSERT INTO appointments (patient_id, doctor_id, appointment_date, status) VALUES (%s,%s,%s,%s);""", (patient_id, doctor_id, appointment_date, status))
        print(f"  ✅ Inserted {count} appointments")
    
    # FINANCE GENERATORS
    def generate_accounts(self, count):
        print(f"\n🏦 Generating {count} accounts...")
        account_types = ['Checking', 'Savings', 'Business', 'Investment']
        currencies = ['USD', 'EUR', 'GBP', 'INR']
        for _ in range(count):
            account_number = f"ACCT-{random.randint(10000000, 99999999)}"
            customer_name = fake.name()
            account_type = random.choice(account_types)
            balance = round(random.uniform(100, 100000), 2)
            self.cursor.execute("""INSERT INTO accounts (account_number, customer_name, account_type, balance) VALUES (%s,%s,%s,%s);""", (account_number, customer_name, account_type, balance))
        print(f"  ✅ Inserted {count} accounts")
    
    def generate_transactions(self, count):
        print(f"\n💸 Generating {count} transactions...")
        self.cursor.execute("SELECT account_id FROM accounts;")
        account_ids = [row[0] for row in self.cursor.fetchall()]
        types = ['DEPOSIT', 'WITHDRAWAL', 'TRANSFER', 'PAYMENT', 'FEE']
        for _ in range(count):
            account_id = random.choice(account_ids) if account_ids else None
            transaction_date = fake.date_time_between(start_date='-1y', end_date='now')
            amount = round(random.uniform(10, 5000), 2)
            transaction_type = random.choice(types)
            self.cursor.execute("""INSERT INTO transactions (account_id, transaction_date, amount, transaction_type) VALUES (%s,%s,%s,%s);""", (account_id, transaction_date, amount, transaction_type))
        print(f"  ✅ Inserted {count} transactions")
    
    def generate_loans(self, count):
        print(f"\n🏦 Generating {count} loans...")
        self.cursor.execute("SELECT account_id FROM accounts;")
        account_ids = [row[0] for row in self.cursor.fetchall()]
        statuses = ['ACTIVE', 'PAID', 'DEFAULTED', 'PENDING']
        for _ in range(count):
            account_id = random.choice(account_ids) if account_ids else None
            loan_amount = round(random.uniform(1000, 50000), 2)
            interest_rate = round(random.uniform(3.5, 12.0), 2)
            status = random.choice(statuses)
            self.cursor.execute("""INSERT INTO loans (account_id, loan_amount, interest_rate, status) VALUES (%s,%s,%s,%s);""", (account_id, loan_amount, interest_rate, status))
        print(f"  ✅ Inserted {count} loans")
    
    # EDUCATION GENERATORS
    def generate_students(self, count):
        print(f"\n🎓 Generating {count} students...")
        majors = ['Computer Science', 'Engineering', 'Business', 'Medicine', 'Law', 'Arts', 'Sciences', 'Mathematics']
        for _ in range(count):
            first_name = fake.first_name()
            last_name = fake.last_name()
            email = f"{first_name.lower()}.{last_name.lower()}@{fake.domain_name()}"
            major = random.choice(majors)
            gpa = round(random.uniform(2.0, 4.0), 2)
            self.cursor.execute("""INSERT INTO students (first_name, last_name, email, major, gpa) VALUES (%s,%s,%s,%s,%s);""", (first_name, last_name, email, major, gpa))
        print(f"  ✅ Inserted {count} students")
    
    def generate_courses(self, count):
        print(f"\n📚 Generating {count} courses...")
        departments = ['CS', 'ENG', 'BIO', 'MATH', 'PHY', 'CHEM', 'HIST', 'PSY']
        course_names = ['Introduction to', 'Advanced', 'Principles of', 'Fundamentals of', 'Modern']
        for _ in range(count):
            dept = random.choice(departments)
            code = f"{dept}{random.randint(100, 499)}"
            course_name = f"{random.choice(course_names)} {fake.word().capitalize()}"
            credits = random.choice([3, 4, 5])
            instructor = fake.name()
            self.cursor.execute("""INSERT INTO courses (course_code, course_name, credits, instructor) VALUES (%s,%s,%s,%s);""", (code, course_name, credits, instructor))
        print(f"  ✅ Inserted {count} courses")
    
    def generate_enrollments(self, count):
        print(f"\n📝 Generating {count} enrollments...")
        self.cursor.execute("SELECT student_id FROM students;")
        student_ids = [row[0] for row in self.cursor.fetchall()]
        self.cursor.execute("SELECT course_id FROM courses;")
        course_ids = [row[0] for row in self.cursor.fetchall()]
        grades = ['A', 'B', 'C', 'D', 'F']
        statuses = ['ENROLLED', 'COMPLETED', 'WITHDRAWN']
        for _ in range(count):
            student_id = random.choice(student_ids) if student_ids else None
            course_id = random.choice(course_ids) if course_ids else None
            grade = random.choice(grades)
            status = random.choice(statuses)
            self.cursor.execute("""INSERT INTO enrollments (student_id, course_id, grade, status) VALUES (%s,%s,%s,%s);""", (student_id, course_id, grade, status))
        print(f"  ✅ Inserted {count} enrollments")
    
    def generate_all(self):
        if not self.connect(): return False
        try:
            self.drop_all_tables()
            self.create_tables()
            self.generate_data()
            print("\n" + "=" * 50)
            print("✅ DATABASE GENERATION COMPLETE!")
            print("=" * 50)
            self.show_summary()
            return True
        except Exception as e:
            print(f"❌ Error: {e}")
            return False
        finally:
            self.disconnect()
    
    def show_summary(self):
        print("\n📊 Database Summary:")
        print("-" * 40)
        domain_data = DOMAINS.get(self.domain, DOMAINS['ecommerce'])
        for table_name in domain_data['tables'].keys():
            try:
                self.cursor.execute(f"SELECT COUNT(*) FROM {table_name};")
                count = self.cursor.fetchone()[0]
                print(f"  {table_name}: {count} rows")
            except:
                print(f"  {table_name}: error reading")
        print("-" * 40)

def main():
    parser = argparse.ArgumentParser(description='Generate PostgreSQL practice database')
    parser.add_argument('--domain', type=str, default='ecommerce', 
                       choices=['ecommerce', 'hr', 'healthcare', 'finance', 'education'],
                       help='Business domain to generate')
    parser.add_argument('--rows', type=int, default=100, help='Number of rows per table')
    args = parser.parse_args()
    
    print("=" * 50)
    print("🗄️  Database Generator")
    print("=" * 50)
    print(f"\n📊 Domain: {DOMAINS[args.domain]['name']}")
    print(f"📋 Rows per table: {args.rows}")
    print("💡 Default password: 4m4teur")
    print()
    
    generator = DatabaseGenerator(args.domain, args.rows)
    generator.generate_all()

if __name__ == "__main__":
    main()
