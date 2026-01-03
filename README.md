# 🇰🇪 Nairobi Air Quality & Weather Data Pipeline

An automated, cloud-native ETL pipeline that monitors Nairobi's atmospheric conditions. This project demonstrates the transition from a local SQLite prototype to a production-ready architecture using Cloud PostgreSQL and GitHub Actions.

## Project Overview
The goal of this project is to provide a reliable, historical record of weather and air quality metrics for Nairobi. The pipeline is fully autonomous, handling data ingestion, cleaning, and storage without manual intervention.

## Project Structure

.
├── .github/
│   └── workflows/
│       └── daily_etl.yml       # The "Brain" (Orchestration)
├── scripts/
│   └── weather_etl.py          # The "Muscle" (Logic)
├── app.py                      # The "Face" (Streamlit Dashboard)
├── requirements.txt            # The "Dependencies"
├── .gitignore                  # The "Privacy Filter"
└── README.md                   # The "Guide"



## The Evolution: From Local to Cloud
This project highlights a significant architectural upgrade:
* **Old Version:** Used local SQLite and `cron` jobs (limited to one machine).
* **Current Version:** Uses **Neon PostgreSQL (Cloud)** and **GitHub Actions** (Global accessibility and high availability).

## Technical Stack
* **Orchestration:** GitHub Actions (CI/CD)
* **Language:** Python 3.12
* **Data Processing:** Pandas
* **Database:** PostgreSQL (Managed via Neon)
* **Interface:** SQLAlchemy (ORM)
* **Visualization:** Streamlit Cloud

## Architecture (ETL)
1. **Extract:** Fetching real-time weather data from the OpenWeatherMap API for Nairobi coordinates.
2. **Transform:** * Sanitizing data types and handling missing values.
    * Calculating derived metrics like the **Heat Index**.
    * Implementing string sanitization for secure database connections.
3. **Load:** Appending cleaned records to a managed PostgreSQL instance with error handling and logging.

## Setup & Installation

### Local Development
1. **Clone the repository:**
   ```bash
   git clone [https://github.com/Migwiian/nrb-air-quality-monitoring-pipeline.git](https://github.com/Migwiian/nrb-air-quality-monitoring-pipeline.git)
   cd nrb-air-quality-monitoring-pipeline
   ```

2.  Setup Virtual Environment:

``` Bash

python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
``` 
3. Configure Secrets: Create a .env file or export your variables: 

``` Bash
export OPENWEATHER_API_KEY='your_api_key'
export DATABASE_URL='postgresql://user:password@host/dbname?sslmode=require'
``` 
4. Run Manually:

``` Bash

python scripts/weather_etl.py
``` 

## Cloud Deployment
The pipeline is automated via .github/workflows/daily_etl.yml. To replicate:

* Add OPENWEATHER_API_KEY and DATABASE_URL to GitHub Repository Secrets.

* The workflow will run daily at 9 PM (UTC) or can be triggered manually via the Actions tab.

## Technical Challenges Overcome
1. Environment Parity: Resolved SQLAlchemy connection errors between local Linux and GitHub Ubuntu-latest runners by implementing strict URL sanitization.

2. Security: Implemented the "Principle of Least Privilege" by using GitHub Secrets instead of hardcoding credentials.

3. CI/CD Resiliency: Optimized GitHub Action YAML to handle specific Personal Access Token (PAT) scopes for workflow updates.