#!/bin/bash

# Check environment variables
if [ -z "$OPENWEATHER_API_KEY" ]; then
    echo "Warning: OPENWEATHER_API_KEY environment variable not set"
    echo "Please set the environment variable: export OPENWEATHER_API_KEY='your_api_key'"
fi

if [ -z "$NYT_API_KEY" ]; then
    echo "Warning: NYT_API_KEY environment variable not set"
    echo "Please set the environment variable: export NYT_API_KEY='your_api_key'"
fi

echo "Initializing database..."
python3 -c "from weather_app.database.schema import DatabaseManager; db = DatabaseManager(); db.create_tables()"

echo "Weather application ready"
echo "Usage: python main.py [command] [options]"
echo "See README.md for detailed instructions"
