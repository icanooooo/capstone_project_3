#!/bin/bash
# init_airflow.sh

# Initialize the Airflow database
airflow db init

# Create the admin user
airflow users create \
    --username airflow \
    --password airflow \
    --firstname Muhammad \
    --lastname Ihsan \
    --role Admin \
    --email muhihsan0@outlook.com

tail -f /dev/null