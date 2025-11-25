import streamlit as st
import pandas as pd
import sqlite3

st.title("Nairobi Weather Dashboard")
st.write("A Simple free Weather dashboard")

conn = sqlite3.connect('weather_data.db')
df = pd.read_sql_query("SELECT * FROM weather_readings ORDER BY timestamp DESC LIMIT 100", conn)

st.line_chart(df.set_index('timestamp')[['temperature', 'humidity']])
st.table(df.head())