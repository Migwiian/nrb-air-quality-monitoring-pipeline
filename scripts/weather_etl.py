# scripts/weather_etl.py
import os
from datetime import datetime, timezone

import pandas as pd
import requests
from sqlalchemy import create_engine, text

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
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    data = response.json()
    if "main" not in data or "weather" not in data or "wind" not in data:
        raise ValueError(f"Unexpected API response shape: {data}")
    return {
        "timestamp": datetime.now(timezone.utc),
        "temperature": data["main"]["temp"],
        "humidity": data["main"]["humidity"],
        "pressure": data["main"]["pressure"],
        "wind_speed": data["wind"]["speed"],
        "weather_condition": data["weather"][0]["description"],
    }

def transform_data(raw_data):
    df = pd.DataFrame([raw_data])
    df["heat_index"] = df["temperature"] + (df["humidity"] * 0.1)
    return df

def create_table_if_missing(engine):
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS weather_readings (
        timestamp TIMESTAMPTZ NOT NULL,
        temperature DOUBLE PRECISION NOT NULL,
        humidity INTEGER NOT NULL,
        pressure INTEGER NOT NULL,
        wind_speed DOUBLE PRECISION NOT NULL,
        weather_condition TEXT NOT NULL,
        heat_index DOUBLE PRECISION NOT NULL
    );
    """
    create_index_sql = """
    CREATE INDEX IF NOT EXISTS weather_readings_timestamp_idx
    ON weather_readings (timestamp);
    """
    with engine.begin() as conn:
        conn.execute(text(create_table_sql))
        conn.execute(text(create_index_sql))

def load_data_to_database(df):
    # 1. Get the connection string from GitHub Secrets / Env
    # Format: postgresql://user:pass@host:port/dbname
    db_url = os.getenv('DATABASE_URL') 
    
    if not db_url:
        raise ValueError("DATABASE_URL not found!")
    
    # If need be, the workflow replaces 'postgres://' with 'postgresql://'
    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)

    # 2. Create the engine
    # We use 'postgresql+psycopg2' to specify the driver
    engine = create_engine(db_url)
    
    # 3. Load data
    # index=False prevents creating a "level_0" column in your DB
    create_table_if_missing(engine)
    df.to_sql("weather_readings", engine, if_exists="append", index=False)

def main():
    raw_data = extract_weather_data()
    df = transform_data(raw_data)
    load_data_to_database(df)
    print("🚀 Data successfully pushed to the Cloud Database!")

if __name__ == "__main__":
    main()
