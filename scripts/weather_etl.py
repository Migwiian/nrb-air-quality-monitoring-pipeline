# scripts/weather_etl.py
import requests
import pandas as pd
import sqlite3
from datetime import datetime
import os
import sqlalchemy
from sqlalchemy import create_engine

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # This block runs when python-dotenv is not installed (e.g., in CI/CD)
    pass
def extract_weather_data():
    lat, lon = -1.2921, 36.8219
    api_key = os.getenv('OPENWEATHER_API_KEY')
    if not api_key:
        raise ValueError("OPENWEATHER_API_KEY environment variable is not set")
    url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}&units=metric"
    response = requests.get(url)
    data = response.json()
    print("API Response:", data)
    return {
        'timestamp': datetime.now(),
        'temperature': data['main']['temp'],
        'humidity': data['main']['humidity'],
        'pressure': data['main']['pressure'],
        'wind_speed': data['wind']['speed'],
        'weather_condition': data['weather'][0]['description']
    }

def transform_data(raw_data):
    df = pd.DataFrame([raw_data])
    df['heat_index'] = df['temperature'] + (df['humidity'] * 0.1)
    return df

import sqlalchemy
from sqlalchemy import create_engine
import os

# ... (keep your extract and transform functions the same)

def load_data_to_database(df):
    # 1. Get the connection string from GitHub Secrets / Env
    # Format: postgresql://user:pass@host:port/dbname
    db_url = os.getenv('DATABASE_URL') 
    
    if not db_url:
        raise ValueError("DATABASE_URL not found!")

    # 2. Create the engine
    # We use 'postgresql+psycopg2' to specify the driver
    engine = create_engine(db_url)
    
    # 3. Load data
    # index=False prevents creating a "level_0" column in your DB
    df.to_sql('weather_readings', engine, if_exists='append', index=False)

def main():
    raw_data = extract_weather_data()
    df = transform_data(raw_data)
    load_data_to_database(df)
    print("🚀 Data successfully pushed to the Cloud Database!")

if __name__ == "__main__":
    main()