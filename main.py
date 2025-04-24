"""
Weather Application Main Module
Provides command-line interface for user interaction
"""
import os
import sys
import argparse
from datetime import datetime, timedelta

from database.schema import DatabaseManager
from database.crud import WeatherCRUD
from api.weather_api import WeatherAPI
from api.news_api import NewsAPI
from exports.data_exporter import DataExporter

class WeatherApp:
    def __init__(self):
        """Initialize weather application"""
        # Initialize 
        self.db_manager = DatabaseManager()
        self.db_manager.create_tables()

        self.crud = WeatherCRUD()

        self.weather_api = WeatherAPI()
        self.news_api = NewsAPI()

        self.exporter = DataExporter()
    
    def run(self):
        """Run the application"""
        parser = argparse.ArgumentParser(description='Weather Application')
        subparsers = parser.add_subparsers(dest='command', help='Available commands')
        
        # Get current weather command
        get_parser = subparsers.add_parser('get', help='Get current weather')
        get_parser.add_argument('location', help='Location name, coordinates, or postal code')
        
        # Get weather forecast command
        forecast_parser = subparsers.add_parser('forecast', help='Get weather forecast')
        forecast_parser.add_argument('location', help='Location name, coordinates, or postal code')
        forecast_parser.add_argument('--days', type=int, default=5, help='Number of forecast days (max 5)')
        
        # Query historical weather command
        query_parser = subparsers.add_parser('query', help='Query historical weather')
        query_parser.add_argument('location', help='Location name')
        query_parser.add_argument('--start', help='Start date (YYYY-MM-DD)', default=(datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d'))
        query_parser.add_argument('--end', help='End date (YYYY-MM-DD)', default=datetime.now().strftime('%Y-%m-%d'))
        
        # Update record command
        update_parser = subparsers.add_parser('update', help='Update weather record')
        update_parser.add_argument('id', type=int, help='Record ID')
        update_parser.add_argument('--temp', type=float, help='Temperature')
        update_parser.add_argument('--humidity', type=int, help='Humidity')
        update_parser.add_argument('--condition', help='Weather condition')
        update_parser.add_argument('--date', help='Date (YYYY-MM-DD)')
        
        # Delete record command
        delete_parser = subparsers.add_parser('delete', help='Delete record')
        delete_parser.add_argument('type', choices=['location', 'weather', 'query'], help='Record type')
        delete_parser.add_argument('id', type=int, help='Record ID')
        
        # List records command
        list_parser = subparsers.add_parser('list', help='List records')
        list_parser.add_argument('type', choices=['locations', 'weather', 'queries'], help='Record type')
        
        # Export data command
        export_parser = subparsers.add_parser('export', help='Export data')
        export_parser.add_argument('format', choices=['json', 'csv', 'xml', 'markdown'], help='Export format')
        export_parser.add_argument('--location', help='Location name (optional)')
        export_parser.add_argument('--output', help='Output file path')
        
        # Get news command
        news_parser = subparsers.add_parser('news', help='Get location-related news')
        news_parser.add_argument('location', help='Location name')
        news_parser.add_argument('--limit', type=int, default=5, help='Number of news items')
        
        args = parser.parse_args()
        
        if args.command == 'get':
            self.get_current_weather(args.location)
        elif args.command == 'forecast':
            self.get_weather_forecast(args.location, args.days)
        elif args.command == 'query':
            self.query_weather_history(args.location, args.start, args.end)
        elif args.command == 'update':
            self.update_weather(args.id, args.temp, args.humidity, args.condition)
        elif args.command == 'delete':
            self.delete_record(args.type, args.id)
        elif args.command == 'list':
            self.list_records(args.type)
        elif args.command == 'export':
            self.export_data(args.format, args.location, args.output)
        elif args.command == 'news':
            self.get_location_news(args.location, args.limit)
        elif args.command == 'update':
            self.update_weather(args.id, args.temp, args.humidity, args.condition, args.date)

        else:
            parser.print_help()
    
    def get_current_weather(self, location):
        """Get current weather
        
        Args:
            location: Location name, coordinates, or postal code
        """
        print(f"Getting current weather for {location}...")
        
        # Get weather from API
        weather_data = self.weather_api.get_current_weather(location)
        if not weather_data:
            print("Failed to get weather data")
            return
        
        # Parse weather
        parsed_data = self.weather_api.parse_weather_data(weather_data)
        if not parsed_data:
            print("Failed to parse weather data")
            return
        
        # Save to database
        location_id = self.crud.create_location(
            parsed_data['location'], 
            parsed_data['latitude'], 
            parsed_data['longitude']
        )
        
        success, result = self.crud.create_weather_record(
            location_id,
            parsed_data['date'],
            parsed_data['temperature'],
            parsed_data['feels_like'],
            parsed_data['humidity'],
            parsed_data['wind_speed'],
            parsed_data['wind_direction'],
            parsed_data['weather_condition'],
            parsed_data['weather_description']
        )
        
        if success:
            print(f"Weather data saved for {parsed_data['location']}")
        

        print("\nCurrent Weather Information:")
        print(f"Location: {parsed_data['location']}, {parsed_data['country']}")
        print(f"Date Time: {parsed_data['date']} {parsed_data['time']}")
        print(f"Temperature: {parsed_data['temperature']}°C (Feels like: {parsed_data['feels_like']}°C)")
        print(f"Humidity: {parsed_data['humidity']}%")
        print(f"Wind Speed: {parsed_data['wind_speed']} m/s ({parsed_data['wind_direction']})")
        print(f"Weather: {parsed_data['weather_description']}")
        print(f"Sunrise: {parsed_data['sunrise']}, Sunset: {parsed_data['sunset']}")
        

        self._ask_for_news(parsed_data['location'])
    
    def get_weather_forecast(self, location, days=5):
        """Get weather forecast
        
        Args:
            location: Location name, coordinates, or postal code
            days: Number of forecast days (max 5)
        """
        print(f"Getting {days}-day weather forecast for {location}...")
        
        # Get forecast data from API
        forecast_data = self.weather_api.get_forecast(location, days)
        if not forecast_data:
            print("Failed to get weather forecast")
            return
        
        # Parse forecast data
        parsed_data = self.weather_api.parse_forecast_data(forecast_data)
        if not parsed_data:
            print("Failed to parse forecast data")
            return
        
        #  city information
        city_info = parsed_data['city']
        print(f"\nCity Information: {city_info['name']}, {city_info['country']}")
        print(f"Coordinates: ({city_info['latitude']}, {city_info['longitude']})")
        print(f"Sunrise: {city_info['sunrise']}, Sunset: {city_info['sunset']}")
        
        #  weather forecast
        daily_forecasts = parsed_data['daily_forecasts']
        print(f"\nWeather forecast for next {min(days, len(daily_forecasts))} days:")
        
        for date, forecasts in daily_forecasts.items():
            if len(daily_forecasts) > days and list(daily_forecasts.keys()).index(date) >= days:
                break
                
            print(f"\n=== {date} ===")
            
            # Calculate avg
            temps = [f['temperature'] for f in forecasts]
            avg_temp = sum(temps) / len(temps)
            
            max_temp = max(temps)
            min_temp = min(temps)
            
            conditions = {}
            for f in forecasts:
                condition = f['weather_condition']
                if condition in conditions:
                    conditions[condition] += 1
                else:
                    conditions[condition] = 1
            
            main_condition = max(conditions.items(), key=lambda x: x[1])[0]
            
            print(f"Average Temperature: {avg_temp:.1f}°C (High: {max_temp:.1f}°C, Low: {min_temp:.1f}°C)")
            print(f"Main Weather: {main_condition}")
            
            # Display 3-hourly forecast
            print("\nHourly Forecast:")
            for forecast in forecasts:
                print(f"  {forecast['time']}: {forecast['temperature']:.1f}°C, {forecast['weather_description']}, Precipitation Chance: {forecast['pop']*100:.0f}%")
        
        self._ask_for_news(city_info['name'])
    
    def query_weather_history(self, location, start_date, end_date):
        """Query historical weather
        
        Args:
            location: Location name
            start_date: Start date
            end_date: End date
        """
        print(f"Querying weather records for {location} from {start_date} to {end_date}...")
        
        # Get location ID
        location_data = self.crud.get_location_by_name(location)
        if not location_data:
            print(f"Location '{location}' does not exist, please get weather for this location first")
            return
        
        location_id = location_data['id']
        
        # Validate date range
        valid, result = self.db_manager.validate_date_range(start_date, end_date)
        if not valid:
            print(f"Invalid date range: {result}")
            return
        
        # Record query history
        self.crud.create_query_history(location_id, start_date, end_date)
        
        # Get weather records
        records = self.crud.get_weather_by_date_range(location_id, start_date, end_date)
        
        if not records:
            print("No weather records found")
            return
        
        print(f"\nFound {len(records)} weather records:")
        for record in records:
            print(f"\nDate: {record['date']}")
            print(f"Location: {record['location_name']}")
            print(f"Temperature: {record['temperature']}°C")
            if record['feels_like']:
                print(f"Feels Like: {record['feels_like']}°C")
            if record['humidity']:
                print(f"Humidity: {record['humidity']}%")
            if record['wind_speed']:
                print(f"Wind Speed: {record['wind_speed']} m/s")
            if record['wind_direction']:
                print(f"Wind Direction: {record['wind_direction']}")
            if record['weather_condition']:
                print(f"Weather: {record['weather_condition']}")
            if record['weather_description']:
                print(f"Weather Description: {record['weather_description']}")
    
    def update_weather(self, record_id, temperature, humidity, condition, date=None):
        """
            record_id: Record ID
            temperature: Temperature
            humidity: Humidity
            condition: Weather condition
            date: Date (YYYY-MM-DD)
        """
        print(f"Updating weather record ID {record_id}...")
        
        # Get original record
        record = self.crud.get_weather_by_id(record_id)
        if not record:
            print(f"Record ID {record_id} does not exist")
            return
        
        # Update record
        success, message = self.crud.update_weather_record(
            record_id,
            temperature,
            None,  # feels
            humidity,
            None,  # wind_speed
            None,  # wind_direction
            condition,
            None,  # weather_description
            date   
        )
        
        if success:
            print(f"Successfully updated record: {message}")
        else:
            print(f"Failed to update record: {message}")
    
    def delete_record(self, record_type, record_id):
        """
        Delete record
        """
        print(f"Deleting {record_type} record ID {record_id}...")
        
        if record_type == 'location':
            success, message = self.crud.delete_location(record_id)
        elif record_type == 'weather':
            success, message = self.crud.delete_weather_record(record_id)
        elif record_type == 'query':
            success, message = self.crud.delete_query_history(record_id)
        else:
            print(f"Unsupported record type: {record_type}")
            return
        
        if success:
            print(f"Successfully deleted record: {message}")
        else:
            print(f"Failed to delete record: {message}")
    
    def list_records(self, record_type):
        """List records
        
        Args:
            record_type: Record type (locations, weather, queries)
        """
        print(f"Listing {record_type} records...")
        
        if record_type == 'locations':
            records = self.crud.get_all_locations()
            if records:
                print(f"\nFound {len(records)} locations:")
                for record in records:
                    print(f"ID: {record['id']}, Name: {record['name']}, Coordinates: ({record['latitude']}, {record['longitude']})")
            else:
                print("No location records found")
        
        elif record_type == 'weather':
            records = self.crud.get_all_weather_records()
            if records:
                print(f"\nFound {len(records)} weather records:")
                for record in records:
                    print(f"ID: {record['id']}, Location: {record['location_name']}, Date: {record['date']}, Temperature: {record['temperature']}°C")
            else:
                print("No weather records found")
        
        elif record_type == 'queries':
            records = self.crud.get_query_history()
            if records:
                print(f"\nFound {len(records)} query history records:")
                for record in records:
                    print(f"ID: {record['id']}, Location: {record['location_name']}, Date Range: {record['start_date']} to {record['end_date']}")
            else:
                print("No query history found")
        
        else:
            print(f"Unsupported record type: {record_type}")
    
    def export_data(self, format_type, location=None, output_path=None):
        """
        Export data
        format_type: Export format (json, csv, xml, markdown)
        """
        print(f"Exporting data in {format_type} format...")
        
        # Get data to export
        if location:
            location_data = self.crud.get_location_by_name(location)
            if not location_data:
                print(f"Location '{location}' does not exist")
                return
            
            records = self.crud.get_weather_by_date_range(
                location_data['id'],
                (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'),
                datetime.now().strftime('%Y-%m-%d')
            )
        else:
            records = self.crud.get_all_weather_records()
        
        if not records:
            print("No data to export")
            return
        
        # Set default output path
        if not output_path:
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            filename = f"weather_data_{timestamp}.{format_type}"
            if format_type == 'markdown':
                filename = f"weather_data_{timestamp}.md"
            output_path = os.path.join(os.getcwd(), filename)
        
        # Export data
        try:
            self.exporter.export_weather_data(records, format_type, output_path)
            print(f"Data successfully exported to: {output_path}")
        except Exception as e:
            print(f"Failed to export data: {e}")
    
    def get_location_news(self, location, limit=5):
        """Get location-related news
        
        Args:
            location: Location name
            limit: Number of news items
        """
        print(f"Getting news related to {location}...")
        
        # Get news
        news = self.news_api.get_location_news(location, limit)
        
        if not news:
            print("No related news found")
            return
        
        print(f"\nFound {len(news)} related news items:")
        for i, article in enumerate(news, 1):
            print(f"\n{i}. {article['title']}")
            print(f"   {article['abstract']}")
            print(f"   Source: {article['source']}, Published Date: {article['published_date']}")
            print(f"   URL: {article['url']}")
    
    def _ask_for_news(self, location):
        """
        Ask user if they want to get local news
        """
        while True:
            response = input(f"\nWould you like to get news related to {location}? (y/n): ").strip().lower()
            if response in ['y', 'yes']:
                self.get_location_news(location)
                break
            elif response in ['n', 'no']:
                break
            else:
                print("Please enter y or n")

if __name__ == "__main__":
    app = WeatherApp()
    app.run()
