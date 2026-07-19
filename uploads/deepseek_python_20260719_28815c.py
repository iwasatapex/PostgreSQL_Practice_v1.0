"""
gym_database_generator.py
Generates a gym database with 3 tables and 100 rows each for SQL practice
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
    "password": "4m4teur",  # Change this to your password
    "host": "localhost",
    "port": "5432"
}

# Number of rows per table
ROWS_PER_TABLE = 100


class GymDatabaseGenerator:
    """Generates a gym database with realistic data."""
    
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
            print("\n💡 Troubleshooting tips:")
            print("  1. Make sure PostgreSQL is running: sudo systemctl start postgresql")
            print("  2. Check your password in DB_SETTINGS")
            print("  3. Default password is: 4m4teur")
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
        tables = ['members', 'trainers', 'workouts']
        for table in tables:
            try:
                self.cursor.execute(f"DROP TABLE IF EXISTS {table} CASCADE;")
                print(f"  Dropped table: {table}")
            except Exception as e:
                print(f"  Error dropping {table}: {e}")
    
    def create_tables(self):
        """Create 3 gym tables."""
        
        print("\n📊 Creating tables...")
        
        # Table 1: Members
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS members (
                member_id SERIAL PRIMARY KEY,
                first_name VARCHAR(50) NOT NULL,
                last_name VARCHAR(50) NOT NULL,
                email VARCHAR(100) UNIQUE,
                phone VARCHAR(20),
                membership_type VARCHAR(30),
                join_date DATE,
                age INTEGER,
                gender VARCHAR(10),
                weight_kg DECIMAL(5,2),
                height_cm INTEGER,
                fitness_goal VARCHAR(50),
                is_active BOOLEAN DEFAULT TRUE
            );
        """)
        print("  ✅ Created: members")
        
        # Table 2: Trainers
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS trainers (
                trainer_id SERIAL PRIMARY KEY,
                first_name VARCHAR(50) NOT NULL,
                last_name VARCHAR(50) NOT NULL,
                email VARCHAR(100) UNIQUE,
                phone VARCHAR(20),
                specialization VARCHAR(50),
                experience_years INTEGER,
                hire_date DATE,
                salary DECIMAL(10,2),
                is_available BOOLEAN DEFAULT TRUE
            );
        """)
        print("  ✅ Created: trainers")
        
        # Table 3: Workouts
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS workouts (
                workout_id SERIAL PRIMARY KEY,
                member_id INTEGER REFERENCES members(member_id),
                trainer_id INTEGER REFERENCES trainers(trainer_id),
                workout_date DATE,
                workout_type VARCHAR(50),
                duration_minutes INTEGER,
                calories_burned INTEGER,
                intensity VARCHAR(20),
                notes TEXT
            );
        """)
        print("  ✅ Created: workouts")
        
        print("\n✅ All 3 tables created successfully!")
    
    def generate_members(self, count=100):
        """Generate member records."""
        print(f"\n💪 Generating {count} members...")
        
        membership_types = ['Basic', 'Premium', 'VIP', 'Student', 'Corporate']
        fitness_goals = ['Weight Loss', 'Muscle Gain', 'Endurance', 'Flexibility', 'General Fitness']
        genders = ['Male', 'Female', 'Other']
        
        members = []
        for _ in range(count):
            first_name = fake.first_name()
            last_name = fake.last_name()
            email = f"{first_name.lower()}.{last_name.lower()}{random.randint(1, 999)}@{fake.domain_name()}"
            phone = fake.phone_number()[:20]
            membership_type = random.choice(membership_types)
            join_date = fake.date_between(start_date='-2y', end_date='today')
            age = random.randint(18, 70)
            gender = random.choice(genders)
            weight_kg = round(random.uniform(50, 150), 1)
            height_cm = random.randint(150, 210)
            fitness_goal = random.choice(fitness_goals)
            is_active = random.choice([True, True, True, False])
            
            members.append((first_name, last_name, email, phone, membership_type, 
                           join_date, age, gender, weight_kg, height_cm, fitness_goal, is_active))
        
        for member in members:
            self.cursor.execute("""
                INSERT INTO members (first_name, last_name, email, phone, membership_type, 
                                   join_date, age, gender, weight_kg, height_cm, fitness_goal, is_active)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
            """, member)
        
        print(f"  ✅ Inserted {count} members")
        return members
    
    def generate_trainers(self, count=100):
        """Generate trainer records."""
        print(f"\n🏋️ Generating {count} trainers...")
        
        specializations = ['Yoga', 'Cardio', 'Strength Training', 'CrossFit', 'Pilates', 
                          'Personal Training', 'Nutrition', 'Rehabilitation', 'Zumba', 'Cycling']
        
        trainers = []
        for _ in range(count):
            first_name = fake.first_name()
            last_name = fake.last_name()
            email = f"trainer.{first_name.lower()}.{last_name.lower()}@{fake.domain_name()}"
            phone = fake.phone_number()[:20]
            specialization = random.choice(specializations)
            experience_years = random.randint(0, 20)
            hire_date = fake.date_between(start_date='-5y', end_date='today')
            salary = round(random.uniform(30000, 80000), 2)
            is_available = random.choice([True, True, True, False])
            
            trainers.append((first_name, last_name, email, phone, specialization, 
                           experience_years, hire_date, salary, is_available))
        
        for trainer in trainers:
            self.cursor.execute("""
                INSERT INTO trainers (first_name, last_name, email, phone, specialization, 
                                   experience_years, hire_date, salary, is_available)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);
            """, trainer)
        
        print(f"  ✅ Inserted {count} trainers")
        return trainers
    
    def generate_workouts(self, count=100):
        """Generate workout records."""
        print(f"\n🏃 Generating {count} workouts...")
        
        # Get member IDs
        self.cursor.execute("SELECT member_id FROM members;")
        member_ids = [row[0] for row in self.cursor.fetchall()]
        
        # Get trainer IDs
        self.cursor.execute("SELECT trainer_id FROM trainers;")
        trainer_ids = [row[0] for row in self.cursor.fetchall()]
        
        workout_types = ['Cardio', 'Strength', 'Yoga', 'HIIT', 'Pilates', 'CrossFit', 
                        'Swimming', 'Cycling', 'Zumba', 'Weight Training']
        intensities = ['Low', 'Medium', 'High', 'Very High']
        
        workouts = []
        for _ in range(count):
            member_id = random.choice(member_ids) if member_ids else None
            trainer_id = random.choice(trainer_ids) if trainer_ids and random.random() > 0.3 else None
            workout_date = fake.date_between(start_date='-1y', end_date='today')
            workout_type = random.choice(workout_types)
            duration_minutes = random.randint(15, 120)
            calories_burned = random.randint(100, 800)
            intensity = random.choice(intensities)
            notes = fake.sentence() if random.random() > 0.5 else None
            
            workouts.append((member_id, trainer_id, workout_date, workout_type, 
                           duration_minutes, calories_burned, intensity, notes))
        
        for workout in workouts:
            self.cursor.execute("""
                INSERT INTO workouts (member_id, trainer_id, workout_date, workout_type, 
                                   duration_minutes, calories_burned, intensity, notes)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
            """, workout)
        
        print(f"  ✅ Inserted {count} workouts")
        return workouts
    
    def generate_all(self, rows=100):
        """Generate all data."""
        if not self.connect():
            return False
        
        try:
            self.drop_tables()
            self.create_tables()
            
            self.generate_members(rows)
            self.generate_trainers(rows)
            self.generate_workouts(rows)
            
            print("\n" + "=" * 50)
            print("✅ GYM DATABASE GENERATION COMPLETE!")
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
        print("\n📊 Gym Database Summary:")
        print("-" * 40)
        
        tables = ['members', 'trainers', 'workouts']
        for table in tables:
            try:
                self.cursor.execute(f"SELECT COUNT(*) FROM {table};")
                count = self.cursor.fetchone()[0]
                print(f"  {table}: {count} rows")
            except:
                print(f"  {table}: error reading")
        
        print("-" * 40)
        print("\n📝 Sample Queries to Try:")
        print("  SELECT * FROM members LIMIT 5;")
        print("  SELECT * FROM trainers WHERE experience_years > 5;")
        print("  SELECT * FROM workouts WHERE calories_burned > 500;")
        print("  SELECT m.first_name, m.last_name, COUNT(w.workout_id) as workouts")
        print("  FROM members m JOIN workouts w ON m.member_id = w.member_id")
        print("  GROUP BY m.member_id ORDER BY workouts DESC LIMIT 10;")
        print("  SELECT t.first_name, t.last_name, AVG(w.calories_burned) as avg_calories")
        print("  FROM trainers t JOIN workouts w ON t.trainer_id = w.trainer_id")
        print("  GROUP BY t.trainer_id ORDER BY avg_calories DESC LIMIT 5;")


def main():
    """Main entry point."""
    print("=" * 50)
    print("🏋️  Gym Database Generator")
    print("=" * 50)
    print(f"\n📊 Generating {ROWS_PER_TABLE} rows per table")
    print("📋 3 tables: members, trainers, workouts")
    print("\n💡 Make sure PostgreSQL is running!")
    print("   sudo systemctl start postgresql")
    print("   Default password: 4m4teur")
    print()
    
    generator = GymDatabaseGenerator()
    generator.generate_all(ROWS_PER_TABLE)


if __name__ == "__main__":
    main()