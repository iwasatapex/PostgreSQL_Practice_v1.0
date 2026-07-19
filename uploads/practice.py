import psycopg2

# Database Connection Settings
DB_SETTINGS = {
    "dbname": "postgres",
    "user": "postgres",
    "password": "yourpassword",
    "host": "localhost",
    "port": "5432"
}

TARGET_SIZE_MB = 300
BATCH_SIZE = 40000  # Shifted down slightly to balance loop processing overhead

def scale_postgres():
    print("Connecting to PostgreSQL...")
    conn = psycopg2.connect(**DB_SETTINGS)
    conn.autocommit = True
    cursor = conn.cursor()

    # 1. Initialize Expert Schema (Exactly 5 tables, 4 columns each)
    print("Creating schema...")
    cursor.execute("""
        DROP TABLE IF EXISTS payments CASCADE;
        DROP TABLE IF EXISTS orders CASCADE;
        DROP TABLE IF EXISTS products CASCADE;
        DROP TABLE IF EXISTS users CASCADE;
        DROP TABLE IF EXISTS logs CASCADE;

        -- 1. Users: Added self-referential id (referred_by_id) for Recursive CTE practice
        CREATE TABLE users (
            user_id SERIAL PRIMARY KEY, username VARCHAR(100), email VARCHAR(100), referred_by_id INT
        );
        
        -- 2. Products: Added JSONB data type for dynamic semi-structured property querying
        CREATE TABLE products (
            product_id SERIAL PRIMARY KEY, product_name VARCHAR(150), price DECIMAL(10,2), specs JSONB
        );
        
        -- 3. Orders: Added Timestamps distributed over 3 years for advanced Window Functions
        CREATE TABLE orders (
            order_id SERIAL PRIMARY KEY, user_id INT, product_id INT, ordered_at TIMESTAMP
        );
        
        -- 4. Payments: Tracks finances matched against order instances
        CREATE TABLE payments (
            transaction_id SERIAL PRIMARY KEY, order_id INT, amount DECIMAL(10,2), transaction_status VARCHAR(20)
        );
        
        -- 5. Logs: Dynamic audit trail mapping operations
        CREATE TABLE logs (
            log_id SERIAL PRIMARY KEY, user_id INT, action_details VARCHAR(100), logged_at TIMESTAMP
        );
    """)

    print("Populating data dynamically via PostgreSQL server engine...")
    
    while True:
        # Check total database size for these 5 tables using pg_relation_size
        cursor.execute("""
            SELECT SUM(pg_relation_size(c.oid)) / (1024.0 * 1024.0)
            FROM pg_class c
            JOIN pg_namespace n ON n.oid = c.relnamespace
            WHERE c.relname IN ('users', 'products', 'orders', 'payments', 'logs')
              AND n.nspname = 'public';
        """)
        current_size_mb = cursor.fetchone()[0] or 0
        
        print(f"Current Database Size: {current_size_mb:.2f} MB / {TARGET_SIZE_MB} MB", end="\r")
        
        if current_size_mb >= TARGET_SIZE_MB:
            break

        # Batch write data using high performance server blocks
        cursor.execute(f"""
            DO $$
            DECLARE
                u_max INT := COALESCE((SELECT MAX(user_id) FROM users), 1);
                p_max INT := COALESCE((SELECT MAX(product_id) FROM products), 1);
                o_max INT := COALESCE((SELECT MAX(order_id) FROM orders), 1);
                
                -- Pool for 30% repeating customers
                u_repeat_pool INT := greatest(1, floor(u_max * 0.3)::INT);
                
                -- Real-world string building arrays
                first_names TEXT[] := ARRAY['John', 'Emma', 'Liam', 'Olivia', 'Noah', 'Ava', 'Oliver', 'Sophia', 'Lucas', 'Mia', 'Ethan', 'Isabella'];
                last_names TEXT[] := ARRAY['Smith', 'Johnson', 'Brown', 'Taylor', 'Miller', 'Wilson', 'Davis', 'Garcia', 'Rodriguez', 'Martinez'];
                brands TEXT[] := ARRAY['Sony', 'Nike', 'Apple', 'Samsung', 'Logitech', 'Adidas', 'Dell', 'Anker', 'Bose'];
                modifiers TEXT[] := ARRAY['Wireless', 'Ergonomic', 'Pro', 'Ultra', 'Smart', 'Premium', 'Eco', 'Portable'];
                items TEXT[] := ARRAY['Headphones', 'Running Shoes', 'Laptop', 'Smartwatch', 'Keyboard', 'Charging Hub', 'Backpack'];
                
                -- JSONB properties variables
                colors TEXT[] := ARRAY['Black', 'White', 'Silver', 'Space Gray'];
                conditions TEXT[] := ARRAY['New', 'Refurbished', 'Open Box'];
                
                actions TEXT[] := ARRAY['login_success', 'password_change', 'view_item', 'logout'];
                statuses TEXT[] := ARRAY['SUCCESS', 'FAILED', 'PENDING'];
                
                fname TEXT;
                lname TEXT;
            BEGIN
                -- 1. Users Loop (Realistic Full Names, 10% Null Emails, Self-Referential Hierarchy)
                FOR g IN 1..{BATCH_SIZE} LOOP
                    fname := first_names[1 + floor(random() * 12)];
                    lname := last_names[1 + floor(random() * 10)];
                    
                    INSERT INTO users (username, email, referred_by_id)
                    VALUES (
                        fname || ' ' || lname,
                        CASE WHEN random() < 0.10 THEN NULL ELSE lower(fname || '.' || lname || g || '@example.com') END, 
                        -- Hierarchical network link: points to a past user id to form tree hierarchies
                        CASE WHEN random() < 0.25 AND u_max > 1 THEN (1 + floor(random() * (u_max - 1)))::INT ELSE NULL END
                    );
                END LOOP;

                -- Refresh user pointer tracking
                u_max := COALESCE((SELECT MAX(user_id) FROM users), 1);
                u_repeat_pool := greatest(1, floor(u_max * 0.3)::INT);

                -- 2. Products (Realistic Names & JSONB object structures map metadata variations)
                INSERT INTO products (product_name, price, specs)
                SELECT 
                    brands[1 + floor(random() * 9)] || ' ' || modifiers[1 + floor(random() * 8)] || ' ' || items[1 + floor(random() * 7)] || ' (V' || g || ')',
                    round((5 + random() * 1495)::numeric, 2),
                    -- Generates dynamic JSON documents payload inline
                    jsonb_build_object(
                        'color', colors[1 + floor(random() * 4)],
                        'condition', conditions[1 + floor(random() * 3)],
                        'warranty_months', (6 + (floor(random() * 4) * 6))::INT
                    )
                FROM generate_series(1, {BATCH_SIZE}) g;

                -- 3. Orders (30% Repeat Customers buying across entire scope, 3-year time series distribution)
                INSERT INTO orders (user_id, product_id, ordered_at)
                SELECT 
                    CASE WHEN random() < 0.30 THEN (1 + floor(random() * u_repeat_pool))::INT 
                         ELSE (1 + floor(random() * u_max))::INT END,
                    (1 + floor(random() * p_max))::INT, 
                    -- Distributes timestamps across the last 1000 days (~3 years)
                    NOW() - (random() * INTERVAL '1000 days')
                FROM generate_series(1, {BATCH_SIZE}) g;

                -- Refresh order pointer tracking
                o_max := COALESCE((SELECT MAX(order_id) FROM orders), 1);

                -- 4. Payments (10% Null status fields)
                INSERT INTO payments (order_id, amount, transaction_status)
                SELECT 
                    (1 + floor(random() * o_max))::INT, 
                    round((20 + random() * 1980)::numeric, 2), 
                    CASE WHEN random() < 0.10 THEN NULL ELSE statuses[1 + floor(random() * 3)] END
                FROM generate_series(1, {BATCH_SIZE}) g;

                -- 5. Logs (10% Null actions, 30% Repeat Users, time series tracking matching timelines)
                INSERT INTO logs (user_id, action_details, logged_at)
                SELECT 
                    CASE WHEN random() < 0.30 THEN (1 + floor(random() * u_repeat_pool))::INT 
                         ELSE (1 + floor(random() * u_max))::INT END,
                    CASE WHEN random() < 0.10 THEN NULL ELSE actions[1 + floor(random() * 4)] END, 
                    NOW() - (random() * INTERVAL '1000 days')
                FROM generate_series(1, {BATCH_SIZE}) g;
            END $$;
        """)

    cursor.close()
    conn.close()
    print(f"\nTarget database scale reached: >= {TARGET_SIZE_MB} MB allocated.")

if __name__ == "__main__":
    scale_postgres()
