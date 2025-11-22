#  Nairobi Weather Data Pipeline

This project collects weather data for Nairobi every 30 minutes and stores it in a database. I built this to learn the basics of data engineering—how to **extract** data from an API, **transform** it, and **load** it into a database (ETL).

---

##  What I Built

The project is an automated ETL pipeline with a monitoring system and a simple visualization layer.

* **Data Collection:** Gets current weather data from the **OpenWeatherMap API**.
* **Data Processing:** Cleans the data and adds **calculated fields** (e.g., heat index).
* **Database Storage:** Stores all historical data in **SQLite**.
* **Monitoring:** Includes logging for errors and data quality issues.
* **Dashboard:** Provides a simple web interface (using Streamlit) to view the collected data.

---

##  Technical Details

The pipeline runs every **30 minutes** using `cron` and follows a basic **ETL pattern**:

1.  **Extract:** Pulls current weather conditions for Nairobi.
2.  **Transform:** Cleans the data and adds derived metrics like **heat index**.
3.  **Load:** Stores data in the database with quality checks.

The project is built entirely with **Python**, utilizing **SQLite**, and the dashboard uses **Streamlit**.

---

##  Setup Instructions

Follow these steps to get the pipeline running locally:

1.  Get an **OpenWeatherMap API key** from their website (free tier is sufficient).
2.  Clone this repository.
3.  Install requirements:
    ```bash
    pip install -r requirements.txt
    ```
4.  Run the ETL once (you will set up the `cron` job later):
    ```bash
    python weather_etl.py
    ```
5.  View the dashboard locally:
    ```bash
    streamlit run app.py
    ```

---

##  What I Learned

This project provided hands-on experience in several key areas of data engineering:

* How to work with APIs and handle common data extraction errors.
* Basic data transformation and manipulation using **pandas**.
* Database operations, schema design, and querying with **SQLite**.
* Setting up automated, scheduled jobs with **cron**.
* Building simple, interactive dashboards with **Streamlit**.