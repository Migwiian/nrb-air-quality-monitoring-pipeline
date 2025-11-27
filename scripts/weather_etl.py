# scripts/weather_etl.py
import requests
import pandas as pd
import sqlite3
from datetime import datetime
import os

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

def load_data_to_database(df, db_name='data/weather_data.db'):
    conn = sqlite3.connect(db_name)
    df.to_sql('weather_readings', conn, if_exists='append', index=False)
    conn.close()

def main():
    raw_data = extract_weather_data()
    df = transform_data(raw_data)
    load_data_to_database(df)
    print("Data loaded successfully!")

if __name__ == "__main__":
    main()