#!/bin/bash

# --- 1. System Update and Essential Tools ---
echo "Updating system packages and installing essentials..."
# 'sudo apt-get install -y' is common for Debian/Ubuntu systems
sudo apt-get update
sudo apt-get install -y python3 python3-pip postgresql libpq-dev

# --- 2. Create Python Virtual Environment ---
echo "Setting up Python environment..."
# 'python3 -m venv venv' creates a clean, isolated environment folder named 'venv'
python3 -m venv venv
# 'source venv/bin/activate' loads the environment so installed packages stay isolated
source venv/bin/activate

# --- 3. Install Python Dependencies ---
echo "Installing Python dependencies (requests, pandas, psycopg2, sqlalchemy)..."
pip install requests pandas psycopg2-binary sqlalchemy 

# --- 4. Setup PostgreSQL Database ---
# Define variables for easy configuration
DB_NAME="nairobi_aq_db"
DB_USER="aq_user"
DB_PASS="StrongPassword123"

echo "Setting up PostgreSQL database: $DB_NAME"
# Create a new database user/role
sudo -u postgres psql -c "CREATE USER $DB_USER WITH PASSWORD '$DB_PASS';"
# Create the specific database and assign ownership to the new user
sudo -u postgres psql -c "CREATE DATABASE $DB_NAME OWNER $DB_USER;"

echo "--- Setup Complete. Database created: $DB_NAME ---"
echo "--- To run the ETL, execute: ./deploy_lab.sh ---"

# Deactivate the virtual environment
deactivate