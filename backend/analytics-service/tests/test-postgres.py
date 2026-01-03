import psycopg2
from psycopg2 import OperationalError

def test_postgres_connection():
    try:
        # Update with your credentials
        connection = psycopg2.connect(
            host="localhost",
            database="analytics_db",
            user="analytics_user",
            password="analytics_pass",
            port="5432"
        )
        
        print("✅ PostgreSQL connection successful!")
        
        # Test basic operations
        cursor = connection.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()
        print(f"PostgreSQL version: {version[0]}")
        
        cursor.execute("SELECT current_database();")
        db_name = cursor.fetchone()
        print(f"Connected to database: {db_name[0]}")
        
        cursor.close()
        connection.close()
        
        return True
        
    except OperationalError as e:
        print(f"❌ PostgreSQL connection failed: {e}")
        return False

if __name__ == "__main__":
    test_postgres_connection()