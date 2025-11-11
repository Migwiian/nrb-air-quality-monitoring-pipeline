import streamlit as st
import pandas as pd
import sqlite3

st.title("🚕 NYC Taxi Insights")
st.write("Simple, free taxi analytics dashboard")

# Simple demo - replace with real data
data = pd.DataFrame({
    'date': pd.date_range('2025-01-01', periods=30),
    'trips': range(1000, 1030)
})

st.line_chart(data.set_index('date'))