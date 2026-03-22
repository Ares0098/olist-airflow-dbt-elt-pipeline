# Use official Airflow image
FROM apache/airflow:2.8.1-python3.9

USER root

# Install system dependencies (optional but safe)
RUN apt-get update && apt-get install -y \
    build-essential \
    && apt-get clean

USER airflow

# Copy requirements
COPY requirements.txt /requirements.txt

# Install Python dependencies
RUN pip install --no-cache-dir -r /requirements.txt