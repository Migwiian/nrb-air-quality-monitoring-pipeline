# scripts/weather_etl.py
import logging
import os
import time
from datetime import datetime, timezone

import pandas as pd
import requests
from sqlalchemy import Column, DateTime, Float, Integer, MetaData, Table, Text as SqlText, create_engine, text
from sqlalchemy.dialects.postgresql import insert

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    # This block runs when python-dotenv is not installed (e.g., in CI/CD)
    pass

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)
logger = logging.getLogger(__name__)


def _heat_index_celsius(temperature_c, humidity_percent):
    """Compute heat index in Celsius using the Rothfusz regression.

    For lower temperature/humidity ranges where the formula is unreliable,
    fall back to actual temperature.
    """
    if temperature_c < 26.7 or humidity_percent < 40:
        return temperature_c

    temperature_f = (temperature_c * 9 / 5) + 32
    rh = humidity_percent
    hi_f = (
        -42.379
        + 2.04901523 * temperature_f
        + 10.14333127 * rh
        - 0.22475541 * temperature_f * rh
        - 0.00683783 * temperature_f**2
        - 0.05481717 * rh**2
        + 0.00122874 * temperature_f**2 * rh
        + 0.00085282 * temperature_f * rh**2
        - 0.00000199 * temperature_f**2 * rh**2
    )
    return (hi_f - 32) * 5 / 9


def extract_weather_data():
    lat, lon = -1.2921, 36.8219
    api_key = os.getenv('OPENWEATHER_API_KEY')
    if not api_key:
        raise ValueError("OPENWEATHER_API_KEY environment variable is not set")
    url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}&units=metric"
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    data = response.json()
    if "main" not in data or "weather" not in data or "wind" not in data or "dt" not in data:
        raise ValueError(f"Unexpected API response shape: {data}")
    reading_timestamp = datetime.fromtimestamp(data["dt"], tz=timezone.utc)
    return {
        "timestamp": reading_timestamp,
        "temperature": data["main"]["temp"],
        "humidity": data["main"]["humidity"],
        "pressure": data["main"]["pressure"],
        "wind_speed": data["wind"]["speed"],
        "weather_condition": data["weather"][0]["description"],
    }

def transform_data(raw_data):
    df = pd.DataFrame([raw_data])
    df["heat_index"] = df.apply(
        lambda row: _heat_index_celsius(row["temperature"], row["humidity"]), axis=1
    )
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
    CREATE UNIQUE INDEX IF NOT EXISTS weather_readings_timestamp_uidx
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
    
    # 3. Load data (idempotent on timestamp)
    create_table_if_missing(engine)
    records = df.to_dict(orient="records")
    if not records:
        logger.warning("No records to insert")
        return 0

    metadata = MetaData()
    weather_table = Table(
        "weather_readings",
        metadata,
        Column("timestamp", DateTime(timezone=True), nullable=False),
        Column("temperature", Float, nullable=False),
        Column("humidity", Integer, nullable=False),
        Column("pressure", Integer, nullable=False),
        Column("wind_speed", Float, nullable=False),
        Column("weather_condition", SqlText, nullable=False),
        Column("heat_index", Float, nullable=False),
    )

    insert_stmt = insert(weather_table).values(records)
    do_nothing_stmt = insert_stmt.on_conflict_do_nothing(index_elements=["timestamp"])

    with engine.begin() as conn:
        result = conn.execute(do_nothing_stmt)
        return result.rowcount or 0

def main():
    start_time = time.monotonic()
    logger.info("Starting ETL run")
    raw_data = extract_weather_data()
    df = transform_data(raw_data)
    inserted = load_data_to_database(df)
    elapsed = time.monotonic() - start_time
    logger.info("ETL completed inserted=%s elapsed_s=%s", inserted, round(elapsed, 2))
    print("Data successfully pushed to the Cloud Database!")

if __name__ == "__main__":
    main()
