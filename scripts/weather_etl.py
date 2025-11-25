import requests
import pandas as pd
import sqlite3
from datetime import datetime
import os # Imported to potentially handle API key from environment

# --- Configuration ---
# Nairobi coordinates (Latitude, Longitude)
NAIROBI_LAT = -1.2921
NAIROBI_LON = 36.8219
# Database file name
DB_NAME = 'weather_data.db'

def extract_weather_data(api_key: str) -> dict:
    """
    Extracts current weather data for Nairobi from the OpenWeatherMap API.

    Parameters
    ----------
    api_key : str
        Your unique OpenWeatherMap API key.

    Returns
    -------
    dict
        A dictionary containing raw weather metrics and a timestamp.
    """
    # 1. Construct the API URL
    url = (
        f"https://api.openweathermap.org/data/2.5/weather?"
        f"lat={NAIROBI_LAT}&lon={NAIROBI_LON}&appid={api_key}&units=metric"
    )

    # 2. Make the API request and parse the JSON response
    try:
        response = requests.get(url)
        response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)
        data = response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error extracting data from API: {e}")
        return None

    # 3. Extract necessary fields into a dictionary
    return {
        'timestamp': datetime.now(),
        'temperature': data['main']['temp'],
        'humidity': data['main']['humidity'],
        'pressure': data['main']['pressure'],
        'wind_speed': data['wind']['speed'],
        'weather_condition': data['weather'][0]['description']
    }

def transform_data(raw_data: dict) -> pd.DataFrame:
    """
    Transforms raw weather data by converting it to a DataFrame and calculating a derived metric.

    Parameters
    ----------
    raw_data : dict
        The raw weather metrics dictionary returned by extract_weather_data().

    Returns
    -------
    pandas.DataFrame
        A DataFrame with cleaned data and a calculated 'heat_index' column.
    """
    # 1. Convert the single dictionary entry into a Pandas DataFrame
    df = pd.DataFrame([raw_data])
    
    # 2. Feature Engineering: Calculate a simple Heat Index
    # NOTE: This is a simplified formula for demonstration, not the official one.
    df['heat_index'] = df['temperature'] + (df['humidity'] * 0.1)

    return df

def load_data_to_database(df: pd.DataFrame, db_name: str = DB_NAME):
    """
    Loads the processed DataFrame into a SQLite database table.

    Parameters
    ----------
    df : pandas.DataFrame
        The DataFrame containing the transformed weather data.
    db_name : str, optional
        The name of the SQLite database file. Defaults to 'weather_data.db'.
    """
    # 1. Connect to the SQLite database (creates the file if it doesn't exist)
    conn = sqlite3.connect(db_name)
    
    # 2. Write the DataFrame to the table 'weather_readings'
    # 'if_exists='append'' ensures new data is added to the end of the table.
    df.to_sql('weather_readings', conn, if_exists='append', index=False)
    
    # 3. Close the connection to save changes and release the file lock
    conn.close()

def main():
    """
    Main execution function that runs the entire ETL pipeline.
    """
    # It is best practice to load the API key from an environment variable (os.environ)
    # or a secure configuration file, not hardcoded.
    api_key = os.environ.get("OPENWEATHER_API_KEY", "YOUR_API_KEY_HERE")
    
    if api_key == "YOUR_API_KEY_HERE":
         print("WARNING: Please set the OPENWEATHER_API_KEY environment variable or replace 'YOUR_API_KEY_HERE' in main().")
         return

    print(f"--- ETL started at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ---")

    # E T L steps
    raw_data = extract_weather_data(api_key)
    if raw_data is None:
        print("ETL failed: Could not extract data.")
        return
        
    df = transform_data(raw_data)
    
    load_data_to_database(df)
    
    print("ETL finished: Data loaded successfully into weather_data.db!")

# --- Script Entry Point ---
if __name__ == "__main__":
    main()