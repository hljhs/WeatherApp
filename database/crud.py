"""
CRUD Operations Implementation
"""
import sqlite3
from datetime import datetime
from .schema import DatabaseManager

class WeatherCRUD:
    def __init__(self):
        """Initialize CRUD operations class"""
        self.db_manager = DatabaseManager()
    
    # CREATE operations
    def create_location(self, name, latitude=None, longitude=None):
        """Create a new location record"""
        try:
            self.db_manager.connect()
            
            # Check if location already exists
            self.db_manager.cursor.execute(
                "SELECT id FROM locations WHERE name = ?", 
                (name,)
            )
            existing = self.db_manager.cursor.fetchone()
            
            if existing:
                return existing['id']  # If location exists, return existing ID
            
            # Create new location
            self.db_manager.cursor.execute(
                "INSERT INTO locations (name, latitude, longitude) VALUES (?, ?, ?)",
                (name, latitude, longitude)
            )
            self.db_manager.conn.commit()
            location_id = self.db_manager.cursor.lastrowid
            return location_id
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return None
        finally:
            self.db_manager.close()
    
    def create_weather_record(self, location_id, date, temperature, feels_like=None, 
                             humidity=None, wind_speed=None, wind_direction=None,
                             weather_condition=None, weather_description=None):
        """Create a new weather record"""
        try:
            self.db_manager.connect()
            
            # Check date format
            valid_date = self.db_manager.validate_date(date)
            if not valid_date:
                return False, "Invalid date format, please use YYYY-MM-DD format"
            
            # Check if location exists
            self.db_manager.cursor.execute(
                "SELECT id FROM locations WHERE id = ?", 
                (location_id,)
            )
            if not self.db_manager.cursor.fetchone():
                return False, "Location ID does not exist"
            
            # Try to insert or update weather record
            try:
                self.db_manager.cursor.execute("""
                INSERT INTO weather_records 
                (location_id, date, temperature, feels_like, humidity, 
                wind_speed, wind_direction, weather_condition, weather_description)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (location_id, date, temperature, feels_like, humidity, 
                     wind_speed, wind_direction, weather_condition, weather_description))
                self.db_manager.conn.commit()
                return True, self.db_manager.cursor.lastrowid
            except sqlite3.IntegrityError:
                # If record exists (unique constraint violation), update it
                self.db_manager.cursor.execute("""
                UPDATE weather_records SET 
                temperature = ?, feels_like = ?, humidity = ?, 
                wind_speed = ?, wind_direction = ?, weather_condition = ?, 
                weather_description = ?, updated_at = CURRENT_TIMESTAMP
                WHERE location_id = ? AND date = ?
                """, (temperature, feels_like, humidity, wind_speed, wind_direction, 
                     weather_condition, weather_description, location_id, date))
                self.db_manager.conn.commit()
                return True, "Record updated"
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return False, f"Database error: {e}"
        finally:
            self.db_manager.close()
    
    def create_query_history(self, location_id, start_date, end_date):
        """Create query history record"""
        try:
            self.db_manager.connect()
            
            # Validate date range
            valid, result = self.db_manager.validate_date_range(start_date, end_date)
            if not valid:
                return False, result
            
            # Check if location exists
            self.db_manager.cursor.execute(
                "SELECT id FROM locations WHERE id = ?", 
                (location_id,)
            )
            if not self.db_manager.cursor.fetchone():
                return False, "Location ID does not exist"
            
            # Create query history record
            self.db_manager.cursor.execute(
                "INSERT INTO query_history (location_id, start_date, end_date) VALUES (?, ?, ?)",
                (location_id, start_date, end_date)
            )
            self.db_manager.conn.commit()
            return True, self.db_manager.cursor.lastrowid
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return False, f"Database error: {e}"
        finally:
            self.db_manager.close()
    
    # READ operations
    def get_location_by_id(self, location_id):
        """Get location information by ID"""
        try:
            self.db_manager.connect()
            self.db_manager.cursor.execute(
                "SELECT * FROM locations WHERE id = ?", 
                (location_id,)
            )
            location = self.db_manager.cursor.fetchone()
            return dict(location) if location else None
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return None
        finally:
            self.db_manager.close()
    
    def get_location_by_name(self, name):
        """Get location information by name"""
        try:
            self.db_manager.connect()
            self.db_manager.cursor.execute(
                "SELECT * FROM locations WHERE name = ?", 
                (name,)
            )
            location = self.db_manager.cursor.fetchone()
            return dict(location) if location else None
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return None
        finally:
            self.db_manager.close()
    
    def get_all_locations(self):
        """Get all location information"""
        try:
            self.db_manager.connect()
            self.db_manager.cursor.execute("SELECT * FROM locations ORDER BY name")
            locations = self.db_manager.cursor.fetchall()
            return [dict(location) for location in locations]
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return []
        finally:
            self.db_manager.close()
    
    def get_weather_by_id(self, record_id):
        """Get weather record by ID"""
        try:
            self.db_manager.connect()
            self.db_manager.cursor.execute("""
            SELECT w.*, l.name as location_name 
            FROM weather_records w
            JOIN locations l ON w.location_id = l.id
            WHERE w.id = ?
            """, (record_id,))
            record = self.db_manager.cursor.fetchone()
            return dict(record) if record else None
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return None
        finally:
            self.db_manager.close()
    
    def get_weather_by_location_and_date(self, location_id, date):
        """Get weather record by location ID and date"""
        try:
            self.db_manager.connect()
            
            # Check date format
            valid_date = self.db_manager.validate_date(date)
            if not valid_date:
                return None
            
            self.db_manager.cursor.execute("""
            SELECT w.*, l.name as location_name 
            FROM weather_records w
            JOIN locations l ON w.location_id = l.id
            WHERE w.location_id = ? AND w.date = ?
            """, (location_id, date))
            record = self.db_manager.cursor.fetchone()
            return dict(record) if record else None
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return None
        finally:
            self.db_manager.close()
    
    def get_weather_by_date_range(self, location_id, start_date, end_date):
        """Get weather records by location ID and date range"""
        try:
            self.db_manager.connect()
            
            # Validate date range
            valid, result = self.db_manager.validate_date_range(start_date, end_date)
            if not valid:
                return []
            
            self.db_manager.cursor.execute("""
            SELECT w.*, l.name as location_name 
            FROM weather_records w
            JOIN locations l ON w.location_id = l.id
            WHERE w.location_id = ? AND w.date BETWEEN ? AND ?
            ORDER BY w.date
            """, (location_id, start_date, end_date))
            records = self.db_manager.cursor.fetchall()
            return [dict(record) for record in records]
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return []
        finally:
            self.db_manager.close()
    
    def get_all_weather_records(self):
        """Get all weather records"""
        try:
            self.db_manager.connect()
            self.db_manager.cursor.execute("""
            SELECT w.*, l.name as location_name 
            FROM weather_records w
            JOIN locations l ON w.location_id = l.id
            ORDER BY w.date DESC
            """)
            records = self.db_manager.cursor.fetchall()
            return [dict(record) for record in records]
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return []
        finally:
            self.db_manager.close()
    
    def get_query_history(self, limit=10):
        """Get query history records"""
        try:
            self.db_manager.connect()
            self.db_manager.cursor.execute("""
            SELECT q.*, l.name as location_name 
            FROM query_history q
            JOIN locations l ON q.location_id = l.id
            ORDER BY q.created_at DESC
            LIMIT ?
            """, (limit,))
            records = self.db_manager.cursor.fetchall()
            return [dict(record) for record in records]
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return []
        finally:
            self.db_manager.close()
    
    # UPDATE operations
    def update_location(self, location_id, name=None, latitude=None, longitude=None):
        """Update location information"""
        try:
            self.db_manager.connect()
            
            # Check if location exists
            self.db_manager.cursor.execute(
                "SELECT * FROM locations WHERE id = ?", 
                (location_id,)
            )
            location = self.db_manager.cursor.fetchone()
            if not location:
                return False, "Location ID does not exist"
            
            # Prepare update data
            update_data = {}
            if name is not None:
                update_data['name'] = name
            if latitude is not None:
                update_data['latitude'] = latitude
            if longitude is not None:
                update_data['longitude'] = longitude
            
            if not update_data:
                return True, "No update data provided"
            
            # Build update SQL
            set_clause = ", ".join([f"{key} = ?" for key in update_data.keys()])
            values = list(update_data.values())
            values.append(location_id)
            
            self.db_manager.cursor.execute(
                f"UPDATE locations SET {set_clause} WHERE id = ?",
                values
            )
            self.db_manager.conn.commit()
            return True, "Location information updated"
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return False, f"Database error: {e}"
        finally:
            self.db_manager.close()
    
    def update_weather_record(self, record_id, temperature=None, feels_like=None, 
                         humidity=None, wind_speed=None, wind_direction=None, 
                         weather_condition=None, weather_description=None, date=None):
        """Update weather record"""
        try:
            self.db_manager.connect()
            
            # Check if record exists
            self.db_manager.cursor.execute(
                "SELECT * FROM weather_records WHERE id = ?", 
                (record_id,)
            )
            record = self.db_manager.cursor.fetchone()
            if not record:
                return False, "Record ID does not exist"
            
            # Build update statement
            update_fields = []
            params = []
            
            if temperature is not None:
                update_fields.append("temperature = ?")
                params.append(temperature)
            
            if feels_like is not None:
                update_fields.append("feels_like = ?")
                params.append(feels_like)
            
            if humidity is not None:
                update_fields.append("humidity = ?")
                params.append(humidity)
            
            if wind_speed is not None:
                update_fields.append("wind_speed = ?")
                params.append(wind_speed)
            
            if wind_direction is not None:
                update_fields.append("wind_direction = ?")
                params.append(wind_direction)
            
            if weather_condition is not None:
                update_fields.append("weather_condition = ?")
                params.append(weather_condition)
            
            if weather_description is not None:
                update_fields.append("weather_description = ?")
                params.append(weather_description)
                
            if date is not None:
                # Validate date format
                valid, result = self.db_manager.validate_date(date)
                if not valid:
                    return False, result
                update_fields.append("date = ?")
                params.append(date)
            
            update_fields.append("updated_at = CURRENT_TIMESTAMP")
            
            if not update_fields:
                return False, "No fields provided for update"
            
            # Execute update
            query = f"UPDATE weather_records SET {', '.join(update_fields)} WHERE id = ?"
            params.append(record_id)
            
            self.db_manager.cursor.execute(query, params)
            self.db_manager.conn.commit()
            
            return True, "Weather record updated"
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return False, f"Database error: {e}"
        finally:
            self.db_manager.close()

    # DELETE operations
    def delete_location(self, location_id):
        """Delete location information (cascade delete related weather records and query history)"""
        try:
            self.db_manager.connect()
            
            # Check if location exists
            self.db_manager.cursor.execute(
                "SELECT * FROM locations WHERE id = ?", 
                (location_id,)
            )
            location = self.db_manager.cursor.fetchone()
            if not location:
                return False, "Location ID does not exist"
            
            # Delete location (foreign key constraints will automatically delete related records)
            self.db_manager.cursor.execute(
                "DELETE FROM locations WHERE id = ?",
                (location_id,)
            )
            self.db_manager.conn.commit()
            return True, "Location and related records deleted"
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return False, f"Database error: {e}"
        finally:
            self.db_manager.close()
    
    def delete_weather_record(self, record_id):
        """Delete weather record"""
        try:
            self.db_manager.connect()
            
            # Check if record exists
            self.db_manager.cursor.execute(
                "SELECT * FROM weather_records WHERE id = ?", 
                (record_id,)
            )
            record = self.db_manager.cursor.fetchone()
            if not record:
                return False, "Record ID does not exist"
            
            # Delete record
            self.db_manager.cursor.execute(
                "DELETE FROM weather_records WHERE id = ?",
                (record_id,)
            )
            self.db_manager.conn.commit()
            return True, "Weather record deleted"
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return False, f"Database error: {e}"
        finally:
            self.db_manager.close()
    
    def delete_query_history(self, query_id):
        """Delete query history record"""
        try:
            self.db_manager.connect()
            
            # Check if record exists
            self.db_manager.cursor.execute(
                "SELECT * FROM query_history WHERE id = ?", 
                (query_id,)
            )
            record = self.db_manager.cursor.fetchone()
            if not record:
                return False, "Query history ID does not exist"
            
            # Delete record
            self.db_manager.cursor.execute(
                "DELETE FROM query_history WHERE id = ?",
                (query_id,)
            )
            self.db_manager.conn.commit()
            return True, "Query history deleted"
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return False, f"Database error: {e}"
        finally:
            self.db_manager.close()
