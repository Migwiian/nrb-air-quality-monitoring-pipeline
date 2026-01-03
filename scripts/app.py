import streamlit as st
import pandas as pd
import sqlite3
import os

# Define the database path relative to the app
DB_PATH = 'data/weather_data.db'
TABLE_NAME = 'weather_readings'

def fetch_data():
    """Fetches the last 100 weather readings from the Cloud Database."""
    try:
        # 1. Establish connection (Uses your DATABASE_URL secret)
        conn = st.connection("postgresql", type="sql")
        
        # 2. Query the cloud DB
        # Streamlit handles the connection closure and the ttl (caching)
        df = conn.query(f"SELECT * FROM {TABLE_NAME} ORDER BY timestamp DESC LIMIT 100", ttl="10m")
        
        if df.empty:
            return None, "Database is empty. Wait for ETL to run."

        # 3. Clean up data for the charts
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df = df.sort_values(by='timestamp', ascending=True).reset_index(drop=True)

        return df, None
    except Exception as e:
        # This catches connection issues, SQL typos, etc.
        return None, f"Pipeline Error: {e}"


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