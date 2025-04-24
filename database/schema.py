"""
Database Schema Definition
"""
import sqlite3
import os
import datetime

class DatabaseManager:
    def __init__(self, db_file='weather.db'):
        """Initialize database manager"""
        self.db_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), db_file)
        self.conn = None
        self.cursor = None
        
    def connect(self):
        """Connect to database"""
        self.conn = sqlite3.connect(self.db_file)
        self.conn.row_factory = sqlite3.Row  # Enable column name access for query results
        self.cursor = self.conn.cursor()
        return self.conn
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
            self.conn = None
            self.cursor = None
    
    def create_tables(self):
        """Create database tables"""
        self.connect()
        
        # Create locations table
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS locations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            latitude REAL,
            longitude REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # Create weather records table
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS weather_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            location_id INTEGER NOT NULL,
            date DATE NOT NULL,
            temperature REAL,
            feels_like REAL,
            humidity INTEGER,
            wind_speed REAL,
            wind_direction TEXT,
            weather_condition TEXT,
            weather_description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (location_id) REFERENCES locations (id) ON DELETE CASCADE,
            UNIQUE(location_id, date)
        )
        ''')
        
        # Create query history table
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS query_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            location_id INTEGER NOT NULL,
            start_date DATE NOT NULL,
            end_date DATE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (location_id) REFERENCES locations (id) ON DELETE CASCADE
        )
        ''')
        
        self.conn.commit()
        self.close()
    
    def validate_date(self, date_str):
        """Validate date format"""
        try:
            return datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            return None
    
    def validate_date_range(self, start_date, end_date):
        """Validate if the date range is valid"""
        start = self.validate_date(start_date)
        end = self.validate_date(end_date)
        
        if not start or not end:
            return False, "Invalid date format, please use YYYY-MM-DD format"
        
        if start > end:
            return False, "Start date cannot be later than end date"
            
        # Check if date range exceeds 30 days (can be adjusted based on requirements)
        if (end - start).days > 30:
            return False, "Date range cannot exceed 30 days"
            
        return True, (start, end)
