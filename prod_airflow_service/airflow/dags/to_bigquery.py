from airflow import DAG
from helper.postgres_app_helper import create_connection, print_query
from airflow.utils.task_group import TaskGroup
from airflow.operators.python import PythonOperator
from datetime import datetime

import pandas as pd
import yaml
import os

def load_config():
    with open("/opt/airflow/dags/configs/app_db.yaml", "r") as file:
        return yaml.safe_load(file)
    
def ingest_data(source_table, temp_storage):
    conn = create_connection("application_postgres", "5432", "application_db", "library_admin", "letsreadbook")

    result, columns = print_query(conn, f"SELECT * FROM {source_table}")

    df = pd.DataFrame(result, columns=columns)
    print(df)

    temp_file_path = os.path.join(temp_storage, f"{source_table}.csv")
    df.to_csv(temp_file_path, index=False)

def create_dag():
    config=load_config()
    temp_storage = config["temp_storage"]["location"]

    os.makedirs(temp_storage, exist_ok=True)

    with DAG(
        "library_postgres_db_to_bigquery",
        start_date=datetime(2024, 12, 15),
        schedule_interval='@once',
        catchup=False) as dag:

        for table in config["tables"]:
            source_table = table["source"]
            destination_table = table["destination"]

            with TaskGroup(f"load_{source_table}", tooltip=f"load {source_table} tasks") as table_group:
                ingest_task=PythonOperator(
                    task_id=f"ingest_{source_table}",
                    python_callable=ingest_data,
                    op_kwargs={
                        "source_table": source_table,
                        "temp_storage": temp_storage,
                    },
                )

                ingest_task
    
    return dag

globals()["library_postgres_db_to_bigquery"] = create_dag()