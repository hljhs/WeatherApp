"""
Weather API Interface Module
For interacting with OpenWeatherMap API to get weather data
"""
import requests
import os
from datetime import datetime

class WeatherAPI:
    def __init__(self, api_key=None):
        """Initialize weather API interface
        
        Args:
            api_key: OpenWeatherMap API key, if None will try to get from environment variables
        """
        self.api_key = api_key or os.environ.get('OPENWEATHER_API_KEY') or "99f286c0e5f8d87ab3b51207174c6547"
        if not self.api_key:
            print("Warning: OpenWeatherMap API key not set, please set OPENWEATHER_API_KEY environment variable or provide during initialization")
        
        self.base_url = "https://api.openweathermap.org/data/2.5"
    
    def get_current_weather(self, location, units="metric"):
        """Get current weather for specified location
        
        Args:
            location: Location name, coordinates or postal code (e.g., "Beijing", "39.9042,116.4074", "100000")
            units: Temperature units (metric: Celsius, imperial: Fahrenheit)
            
        Returns:
            dict: Dictionary containing weather information, returns None if failed
        """
        if not self.api_key:
            return None
            
        # Check if location is in coordinate format
        if ',' in location and all(part.replace('.', '', 1).replace('-', '', 1).isdigit() 
                                  for part in location.split(',')):
            lat, lon = location.split(',')
            endpoint = f"{self.base_url}/weather?lat={lat.strip()}&lon={lon.strip()}"
        # Check if location is in postal code format
        elif location.isdigit():
            endpoint = f"{self.base_url}/weather?zip={location}"
        else:
            endpoint = f"{self.base_url}/weather?q={location}"
            
        endpoint += f"&appid={self.api_key}&units={units}&lang=en"
        
        try:
            response = requests.get(endpoint)
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Failed to get weather data: {response.status_code} - {response.text}")
                return None
        except Exception as e:
            print(f"Error requesting weather API: {e}")
            return None
    
    def get_forecast(self, location, days=5, units="metric"):
        """Get weather forecast for specified location
        
        Args:
            location: Location name, coordinates or postal code (e.g., "Beijing", "39.9042,116.4074", "100000")
            days: Number of forecast days (maximum 5)
            units: Temperature units (metric: Celsius, imperial: Fahrenheit)
            
        Returns:
            dict: Dictionary containing forecast information, returns None if failed
        """
        if not self.api_key:
            return None
            
        # Check if location is in coordinate format
        if ',' in location and all(part.replace('.', '', 1).replace('-', '', 1).isdigit() 
                                  for part in location.split(',')):
            lat, lon = location.split(',')
            endpoint = f"{self.base_url}/forecast?lat={lat.strip()}&lon={lon.strip()}"
        # Check if location is in postal code format
        elif location.isdigit():
            endpoint = f"{self.base_url}/forecast?zip={location}"
        else:
            endpoint = f"{self.base_url}/forecast?q={location}"
            
        endpoint += f"&appid={self.api_key}&units={units}&lang=en"
        
        try:
            response = requests.get(endpoint)
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Failed to get weather forecast: {response.status_code} - {response.text}")
                return None
        except Exception as e:
            print(f"Error requesting weather API: {e}")
            return None
    
    def parse_weather_data(self, weather_data):
        """Parse weather data into application format
        
        Args:
            weather_data: Raw weather data from API
            
        Returns:
            dict: Formatted weather data
        """
        if not weather_data:
            return None
            
        try:
            # Extract main weather information
            result = {
                'location': weather_data.get('name', 'Unknown'),
                'country': weather_data.get('sys', {}).get('country', ''),
                'latitude': weather_data.get('coord', {}).get('lat'),
                'longitude': weather_data.get('coord', {}).get('lon'),
                'temperature': weather_data.get('main', {}).get('temp'),
                'feels_like': weather_data.get('main', {}).get('feels_like'),
                'humidity': weather_data.get('main', {}).get('humidity'),
                'pressure': weather_data.get('main', {}).get('pressure'),
                'wind_speed': weather_data.get('wind', {}).get('speed'),
                'wind_direction': self._get_wind_direction(weather_data.get('wind', {}).get('deg')),
                'clouds': weather_data.get('clouds', {}).get('all'),
                'weather_condition': weather_data.get('weather', [{}])[0].get('main', 'Unknown'),
                'weather_description': weather_data.get('weather', [{}])[0].get('description', 'Unknown'),
                'weather_icon': weather_data.get('weather', [{}])[0].get('icon'),
                'timestamp': weather_data.get('dt'),
                'date': datetime.fromtimestamp(weather_data.get('dt', 0)).strftime('%Y-%m-%d'),
                'time': datetime.fromtimestamp(weather_data.get('dt', 0)).strftime('%H:%M:%S'),
                'sunrise': datetime.fromtimestamp(weather_data.get('sys', {}).get('sunrise', 0)).strftime('%H:%M:%S'),
                'sunset': datetime.fromtimestamp(weather_data.get('sys', {}).get('sunset', 0)).strftime('%H:%M:%S')
            }
            return result
        except Exception as e:
            print(f"Error parsing weather data: {e}")
            return None
    
    def parse_forecast_data(self, forecast_data):
        """Parse forecast data into application format
        
        Args:
            forecast_data: Raw forecast data from API
            
        Returns:
            dict: Formatted forecast data
        """
        if not forecast_data:
            return None
            
        try:
            # Extract city information
            city_info = {
                'name': forecast_data.get('city', {}).get('name', 'Unknown'),
                'country': forecast_data.get('city', {}).get('country', ''),
                'latitude': forecast_data.get('city', {}).get('coord', {}).get('lat'),
                'longitude': forecast_data.get('city', {}).get('coord', {}).get('lon'),
                'timezone': forecast_data.get('city', {}).get('timezone'),
                'sunrise': datetime.fromtimestamp(forecast_data.get('city', {}).get('sunrise', 0)).strftime('%H:%M:%S'),
                'sunset': datetime.fromtimestamp(forecast_data.get('city', {}).get('sunset', 0)).strftime('%H:%M:%S')
            }
            
            # Extract forecast list
            forecast_list = forecast_data.get('list', [])
            
            # Organize forecast data by date
            daily_forecasts = {}
            for item in forecast_list:
                # Get date
                dt = datetime.fromtimestamp(item.get('dt', 0))
                date = dt.strftime('%Y-%m-%d')
                time = dt.strftime('%H:%M:%S')
                
                # Extract weather information
                weather_info = {
                    'time': time,
                    'temperature': item.get('main', {}).get('temp'),
                    'feels_like': item.get('main', {}).get('feels_like'),
                    'temp_min': item.get('main', {}).get('temp_min'),
                    'temp_max': item.get('main', {}).get('temp_max'),
                    'pressure': item.get('main', {}).get('pressure'),
                    'humidity': item.get('main', {}).get('humidity'),
                    'weather_condition': item.get('weather', [{}])[0].get('main', 'Unknown'),
                    'weather_description': item.get('weather', [{}])[0].get('description', 'Unknown'),
                    'weather_icon': item.get('weather', [{}])[0].get('icon'),
                    'clouds': item.get('clouds', {}).get('all'),
                    'wind_speed': item.get('wind', {}).get('speed'),
                    'wind_direction': self._get_wind_direction(item.get('wind', {}).get('deg')),
                    'visibility': item.get('visibility'),
                    'pop': item.get('pop')  # Probability of precipitation
                }
                
                # Add weather information to corresponding date
                if date not in daily_forecasts:
                    daily_forecasts[date] = []
                daily_forecasts[date].append(weather_info)
            
            # Combine results
            result = {
                'city': city_info,
                'daily_forecasts': daily_forecasts
            }
            
            return result
        except Exception as e:
            print(f"Error parsing forecast data: {e}")
            return None
    
    def _get_wind_direction(self, degrees):
        """Get wind direction description based on degrees
        
        Args:
            degrees: Wind direction in degrees
            
        Returns:
            str: Wind direction description
        """
        if degrees is None:
            return "Unknown"
            
        directions = ["North", "Northeast", "East", "Southeast", "South", "Southwest", "West", "Northwest"]
        index = round(degrees / 45) % 8
        return directions[index]
