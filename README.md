# Weather App Documentation 

## 1. Project Overview

This project is a weather application that allows users to input location data and retrieve current weather information & news. It supports full CRUD operations, API integration for weather and news data, and multi-format data export.

### 1.1 Features

- **CRUD Operations**:Full support for creating, reading, updating, and deleting weather records
- **API Integration**: Fetches weather from OpenWeatherMap and news from New York Times
- **Data Export**: Supports exporting weather data in JSON, CSV, XML, and Markdown
- **Multi Input**：Supports input via city name, coordinates, or postal code

### 1.2 Tech Stack
The project is build based on Python, and use SQLite as DatabaseManager

## 2. System Structure

```
weather_app_no_frontend/
├── api/                  # API modules
│   ├── news_api.py       # News API integration
│   └── weather_api.py    # Weather API integration
├── database/             # Database modules
│   ├── __init__.py       
│   ├── crud.py           # CRUD implementation
│   └── schema.py         # DB schema definitions
├── exports/              # Export modules
│   └── data_exporter.py  # Data export
├── tests/                # test modules
│   ├── __init__.py
│   └── test_crud.py      # CRUD test
├── __init__.py           
├── main.py               # main (run this)
├── README.md             
└── setup.sh              
```

## 3. Usage Guide

### 3.1 Environment Setting

The project currently uses default free API endpoints. However, if the free API expires or the user wishes to use a paid API for more features, environment variables can be set as follows:

```bash
# OpenWeatherMap 
export OPENWEATHER_API_KEY="your_api_key"

# New York Times 
export NYT_API_KEY="your_api_key"
```

### 3.2 Install Dependencies

```bash
pip install requests
```

### 3.3 Initialization

```bash
# Use setup script
./weather_app_no_frontend/setup.sh

# Or manually initialize DB
python -c "from weather_app_no_frontend.database.schema import DatabaseManager; db = DatabaseManager(); db.create_tables()"
```

### 3.4 Command Line Usage


#### Get Current Weather

```bash
python main.py get <location>
```

example:
```bash
# location name
python main.py get Shanghai # add "" if location name is more than one word
# longitude and latitude
python main.py get "39.9042,116.4074" 
# zip code
python main.py get 100000  
```

#### Get Weather Forecast

```bash
python main.py forecast <location> [--days <days>]
```

example:
```bash
python main.py forecast Shanghai # DEFAULT DAY 5
python main.py forecast Shanghai --days 3 
```

#### Get Historical Weather

**IMPORTANT**: Under the default API, only previously queried weather data can be retrieved as historical records. Direct access to historical weather is not supported because the free API does not provide this feature. 
To use the historical weather query functionality, you need to switch to a paid API.

```bash
python main.py query <location> [--start <start_date>] [--end <end_date>]
```

example:
```bash
python main.py query Shanghai
python main.py query Shanghai --start 2025-04-01 --end 2025-04-24
```

#### Update Record

```bash
python main.py update <id> [--temp <temperature>] [--humidity <humidity>] [--condition <condition>]
```

example:
```bash
python main.py update 1 --temp 26.5 --humidity 70 --condition Cloudy
```

#### Delete Record

```bash
python main.py delete <type> <id>
```

example:
```bash
python main.py delete weather 1
python main.py delete location 2
python main.py delete query 3
```

#### List Record

```bash
python main.py list <type>
```

example:
```bash
python main.py list locations
python main.py list weather
python main.py list queries
```

#### Export Data

```bash
python main.py export <format> [--location <location>] [--output <output_path>]
```

example:
```bash
python main.py export json
python main.py export csv --location Shanghai
python main.py export xml --output /path/to/output.xml
```

#### Get Local News

```bash
python main.py news <location> [--limit <limit>]
```

example:
```bash
python main.py news Shanghai
python main.py news Shanghai --limit 10
```

## 4. Others:
The author of this project is Lijian Huang. 
Description of the PM Accelerator (from LinkedIn ): The Product Manager Accelerator Program is designed to support PM professionals through every stage of their careers. From students looking for entry-level jobs to Directors looking to take on a leadership role, our program has helped over hundreds of students fulfill their career aspirations.
