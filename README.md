# 🇰🇪 Nairobi Air Quality & Weather Data Pipeline

This project collects weather data for Nairobi every 30 minutes and stores it in a database. I built this to learn the basics of data engineering—how to **extract** data from an API, **transform** it, and **load** it into a database (ETL).

---

## 🚀 What I Built

The project is an automated ETL pipeline with a monitoring system and a simple visualization layer.

* **Data Collection:** Gets current weather data from the [OpenWeatherMap API](https://openweathermap.org/api).
* **Data Processing:** Cleans the data and adds **calculated fields** (e.g., heat index).
* **Database Storage:** Stores all historical data in **SQLite** (`data/weather_data.db`).
* **Monitoring:** Includes logging for errors and data quality issues, stored in a dedicated log file.
* **Dashboard:** Provides a simple web interface (using Streamlit) to view the collected data.

---

## 🛠️ Technical Details

The pipeline runs every **30 minutes** using a **cron job** and follows a basic **ETL pattern**:

* **Extract:** Pulls current weather conditions for Nairobi.
* **Transform:** Cleans the data and adds derived metrics like **heat index**.
* **Load:** Stores data in the database with quality checks.

The project is built entirely with **Python**, utilizing **SQLite**, and the dashboard uses **Streamlit**.

---

## ⚙️ Setup Instructions

Follow these steps to get the pipeline running locally:

### A. Environment Setup

1.  **Clone** this repository.
    ```bash
    git clone [YOUR_REPO_URL]
    cd nrb-air-quality-monitoring-pipeline
    ```
2.  **Create and activate** the Python virtual environment (`venv`).
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```
3.  **Install requirements:**
    ```bash
    pip install -r requirements.txt
    ```

### B. Initial Run & API Configuration

1.  Get an **OpenWeatherMap API key** from their website (free tier is sufficient).
2.  **Set the API Key** and run the ETL once to create the database file and confirm setup.
    ```bash
    export OPENWEATHER_API_KEY='YOUR_API_KEY_HERE'
    python scripts/weather_etl.py
    ```

### C. Automation with Cron

To set up the automated scheduler (which runs every 30 minutes):

1.  **Install Cron** (if necessary, e.g., in Codespaces):
    ```bash
    sudo apt update && sudo apt install cron -y
    sudo service cron start
    ```
2.  **Create the logs directory:**
    ```bash
    mkdir -p logs
    ```
3.  **Edit your crontab** with `crontab -e` and paste the job command (replace the placeholder with your actual API key):
    ```cron
    */30 * * * * bash -c 'export OPENWEATHER_API_KEY="YOUR_API_KEY_HERE" && /workspaces/nrb-air-quality-monitoring-pipeline/venv/bin/python /workspaces/nrb-air-quality-monitoring-pipeline/scripts/weather_etl.py >> /workspaces/nrb-air-quality-monitoring-pipeline/logs/weather_etl.log 2>&1'
    ```
4.  **Monitor the run** and check the log file for success:
    ```bash
    cat logs/weather_etl.log
    ```

### D. Dashboard

View the dashboard locally:
```bash
streamlit run app.py
```