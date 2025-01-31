from helper.webscraper_helper import get_data_asetku, create_asetku_dataframe
from helper.bigquery_helper import load_bigquery, create_schema, create_table, create_client, create_dataset
from helper.pandas_helper import automatically_change_dtypes
from helper.alert_helper import send_failure_to_discord
from datetime import timedelta, datetime
from airflow import DAG
from airflow.operators.python_operator import PythonOperator

import pandas as pd

import yaml
import os

def load_config():
    with open("/opt/airflow/dags/configs/app_db.yaml", "r") as file:
        return yaml.safe_load(file)

def get_data(temp_storage):
    category, asetku_data = get_data_asetku('https://www.asetku.co.id/')

    df = create_asetku_dataframe(asetku_data)

    temp_file_path = os.path.join(temp_storage, "asetku_data.csv")
    df.to_csv(temp_file_path, index=False)

def input_to_bigquery_table(table_id, temp_storage):
    client = create_client()

    dataframe = pd.read_csv(f"{temp_storage}/asetku_data.csv")

    dataframe = automatically_change_dtypes(dataframe)

    try:
        create_table(client, table_id, create_schema(dataframe))
    except:
        print("Table already exist")

    load_bigquery(client, dataframe, table_id, "WRITE_APPEND")

def create_dag():
    default_args = {
        'owner' : 'ican',
        'retries' : 1,
        'retry_delay' : timedelta(minutes=1),
        'on_failure_callback' : send_failure_to_discord,
    }
    config = load_config()
    table_id = config["bigquery"]["project"] + "." + config["bigquery"]["dataset"] + "." + "ihsan_webscrape"
    temp_storage = config["temp_storage"]["location"]

    with DAG(
        "asetku_webscrapping_dag",
        start_date=datetime(2025, 1, 30),
        tags=['bigquery_dags'],
        default_args=default_args,
        schedule_interval='@daily',
        catchup=False) as dag:

        get_data_task = PythonOperator(
            task_id='get_data_task',
            python_callable=get_data,
            op_kwargs={
                "temp_storage": temp_storage
            }
        )

        input_to_bigquery_task = PythonOperator(
            task_id='to_bigquery_task',
            python_callable=input_to_bigquery_table,
            op_kwargs={
                "table_id": table_id,
                "temp_storage": temp_storage
            }            
        )

        get_data_task >> input_to_bigquery_task

    return dag

dag = create_dag()


    



