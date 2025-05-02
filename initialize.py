from db import create_tables
import os

def initialize_database():
    # Create data directory if needed
    os.makedirs('data', exist_ok=True)
    
    # Initialize database and tables
    create_tables()
    print("Database initialized successfully!")

if __name__ == "__main__":
    initialize_database()