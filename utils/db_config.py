from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
import os
from dotenv import load_dotenv
import time

# Load environment variables
load_dotenv()

# Database connection configuration
DB_USER = os.getenv('DB_USER', 'twilio_user')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'your_password')
DB_HOST = os.getenv('DB_HOST', 'mysql')
DB_PORT = os.getenv('DB_PORT', '3306')
DB_NAME = os.getenv('DB_NAME', 'lendingkart_db')

# Create database URL
DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

def create_connection(max_retries=5, retry_delay=5):
    """Create and return a database connection with retry logic."""
    for attempt in range(max_retries):
        try:
            engine = create_engine(DATABASE_URL)
            # Test the connection
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            return engine
        except SQLAlchemyError as e:
            if attempt < max_retries - 1:
                print(f"Connection attempt {attempt + 1} failed. Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                print(f"Error creating database connection after {max_retries} attempts: {str(e)}")
                return None

def execute_query(query: str, params: dict = None):
    """Execute a single SQL query and return results."""
    engine = create_connection()
    if not engine:
        return []
    
    try:
        with engine.connect() as connection:
            result = connection.execute(text(query), params or {})
            if result.returns_rows:
                rows = result.fetchall()
                column_names = result.keys()
                return [dict(zip(column_names, row)) for row in rows]
            return {"affected_rows": result.rowcount}
    except SQLAlchemyError as e:
        print(f"Error executing query: {query}")
        print(f"Error details: {str(e)}")
        return {"error": str(e)}
    finally:
        engine.dispose() 