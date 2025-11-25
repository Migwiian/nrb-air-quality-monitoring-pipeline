import streamlit as st
import pandas as pd
import sqlite3
import os

# Define the database path relative to the app
DB_PATH = 'data/weather_data.db'
TABLE_NAME = 'weather_readings'

def fetch_data():
    """Fetches the last 100 weather readings from the SQLite database."""
    # Ensure the data directory exists (though the ETL script should handle this)
    if not os.path.exists('data'):
        return None, "Data directory not found. Run ETL first."

    # Check if the database file exists
    if not os.path.exists(DB_PATH):
        return None, f"Database file '{DB_PATH}' not found. Run the ETL pipeline."

    try:
        conn = sqlite3.connect(DB_PATH)
        # Fetch the last 100 records ordered by timestamp descending
        query = f"SELECT * FROM {TABLE_NAME} ORDER BY timestamp DESC LIMIT 100"
        df = pd.read_sql_query(query, conn)
        conn.close()

        # Convert timestamp to datetime and ensure correct order (oldest first for charts)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df = df.sort_values(by='timestamp', ascending=True).reset_index(drop=True)

        return df, None
    except sqlite3.OperationalError as e:
        # Catch errors like 'no such table'
        return None, f"Database operational error: {e}. Check if the '{TABLE_NAME}' table exists."
    except Exception as e:
        return None, f"An unexpected error occurred: {e}"


st.set_page_config(
    page_title="Nairobi Weather Data",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("🇰🇪 Nairobi Weather Data Pipeline Dashboard")
st.markdown("A real-time monitoring dashboard for weather data collected every 30 minutes via the ETL pipeline.")

data, error = fetch_data()

if error:
    # Display error if data retrieval fails
    st.error(f"Data Loading Error: {error}")
    st.info("Please ensure the ETL pipeline has been run at least once to create the database.")
else:
    # Reverse the order for metrics/table display (most recent at top)
    df_metrics = data.sort_values(by='timestamp', ascending=False)
    
    # 1. Display Key Metrics from the latest reading
    if not df_metrics.empty:
        latest_reading = df_metrics.iloc[0]
        st.subheader("Current Conditions")
        
        # Use columns for a clean, responsive layout
        col1, col2, col3, col4 = st.columns(4)

        col1.metric("Temperature (°C)", f"{latest_reading['temperature']:.1f}")
        col2.metric("Humidity (%)", f"{latest_reading['humidity']:.0f}")
        col3.metric("Wind Speed (m/s)", f"{latest_reading['wind_speed']:.1f}")
        col4.metric("Pressure (hPa)", f"{latest_reading['pressure']:.0f}")
        
        st.divider()

    # 2. Display Charts (Temperature and Humidity over time)
    st.subheader("Historical Trends (Last 100 Readings)")
    
    # Use the ascending dataframe 'data' for correct time-series plotting
    if not data.empty:
        chart_data = data.set_index('timestamp')[['temperature', 'humidity']]
        st.line_chart(chart_data)
    else:
        st.warning("No data found in the database table.")


    # 3. Display Raw Data Table
    st.subheader("Raw Data Table")
    # Use st.dataframe for a more interactive and visually appealing table
    st.dataframe(
        df_metrics, 
        use_container_width=True,
        # Hide the system-generated columns for cleanliness
        column_order=['timestamp', 'temperature', 'humidity', 'pressure', 'wind_speed', 'description'],
        hide_index=True
    )