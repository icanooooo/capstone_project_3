from airflow import DAG
from helper.postgres_app_helper import create_connection, print_query
from helper.bigquery_helper import create_client, upsert_data, incremental_load, check_dataset, create_dataset
from helper.pandas_helper import automatically_change_dtypes
from airflow.utils.task_group import TaskGroup
from airflow.operators.python import PythonOperator
from airflow.exceptions import AirflowSkipException
from datetime import datetime

import pandas as pd
import yaml
import os
import pytz

def load_config():
    with open("/opt/airflow/dags/configs/app_db.yaml", "r") as file:
        return yaml.safe_load(file)

def check_dataset_exist(project_id, dataset_id):
    result = check_dataset(project_id, dataset_id)

    if result:
        print(f"{dataset_id} already exist")
        status = True
    else:
        status = False

    return {'status': status} #return must be in json format

def creating_dataset(project_id, dataset_id, **kwargs):
    ti = kwargs['ti']
    status = ti.xcom_pull(task_ids='check_dataset')['status']

    if status:
        raise AirflowSkipException(f"skipping as {dataset_id} already exist")
    else:
        print(f"dataset does not exist, proceed in creating dataset")
        create_dataset(project_id, dataset_id)  


def ingest_data(source_table, temp_storage):
    conn = create_connection("application_postgres", "5432", "application_db", "library_admin", "letsreadbook")

    result, columns = print_query(conn, f"SELECT * FROM {source_table} WHERE created_at = CURRENT_DATE - INTERVAL '1 day';") # Jangan lupa untuk where h-1

    df = pd.DataFrame(result, columns=columns)

    temp_file_path = os.path.join(temp_storage, f"{source_table}.csv")
    df.to_csv(temp_file_path, index=False)

def load_stg_table(source_table, temp_storage, project_id, dataset_id, destination):
    client = create_client()
    dataframe = pd.read_csv(f"{temp_storage}/{source_table}.csv")
    dataframe['created_at'] = pd.to_datetime(dataframe['created_at']) # ini jangan UTC Pastiin
    dataframe['created_at'] = dataframe['created_at'].dt.tz_localize(None) 

    dataframe = automatically_change_dtypes(dataframe)

    table_id = f"{project_id}.{dataset_id}.{destination}"

    incremental_load(client, dataframe, table_id, "WRITE_APPEND", "created_at")

    print(f"loaded {dataframe.shape[0]} row to {destination}")

def upsert_table(temp_storage, source_table, project_id, dataset_id, stage_id, destination_id):
    client = create_client()

    dataframe = pd.read_csv(f"{temp_storage}/{source_table}.csv")
    dataframe['created_at'] = pd.to_datetime(dataframe['created_at']) # ini jangan UTC Pastiin
    dataframe['created_at'] = dataframe['created_at'].dt.tz_localize(None)

    dataframe = automatically_change_dtypes(dataframe)

    stage_table = f"{project_id}.{dataset_id}.{stage_id}"
    dest_table = f"{project_id}.{dataset_id}.{destination_id}"

    upsert_data(client, stage_table, dest_table, "id", dataframe, "created_at")

def create_dag():
    config=load_config()
    temp_storage = config["temp_storage"]["location"]
    project_id = config["bigquery"]["project"]
    dataset_id = config["bigquery"]["dataset"]

    os.makedirs(temp_storage, exist_ok=True)

    with DAG(
        "library_postgres_db_to_bigquery",
        start_date=datetime(2024, 12, 20),
        tags=['bigquery_dags'],
        schedule_interval='15 * * * *', # setiap jam dalam menit ke 15 (01.15, 02.15, seterusnya..)
        catchup=False) as dag:

        check_dataset_task = PythonOperator(
            task_id=f"check_dataset",
            python_callable=check_dataset_exist,
            op_kwargs={
                "project_id": project_id,
                "dataset_id": dataset_id,
            },
        )

        create_dataset_task = PythonOperator(
            task_id=f"create_dataset",
            python_callable=creating_dataset,
            op_kwargs={
                "project_id": project_id,
                "dataset_id": dataset_id,
            },
        )

        grouped_task = []

        for table in config["tables"]:
            source_table = table["source"]
            staging_table = table["staging_table"]
            destination_bq = table["destination"]

            with TaskGroup(f"load_{source_table}", tooltip=f"load {source_table} tasks") as table_group:
                ingest_task=PythonOperator(
                    task_id=f"ingest_{source_table}",
                    python_callable=ingest_data,
                    op_kwargs={
                        "source_table": source_table,
                        "temp_storage": temp_storage,
                    },
                    trigger_rule="none_failed"
                )

                insert_stg_bq=PythonOperator(
                    task_id=f"stg_table_{destination_bq}",
                    python_callable=load_stg_table,
                    op_kwargs={
                        "source_table": source_table,
                        "temp_storage": temp_storage,
                        "project_id": project_id,
                        "dataset_id": dataset_id,
                        "destination": staging_table
                    }
                )

                upsert_to_bq=PythonOperator(
                    task_id=f"upsert_{destination_bq}",
                    python_callable=upsert_table,
                    op_kwargs={
                        "temp_storage": temp_storage,
                        "source_table": source_table,
                        "project_id": project_id,
                        "dataset_id": dataset_id,
                        "stage_id": staging_table,
                        "destination_id": destination_bq
                    }
                )

                ingest_task >> insert_stg_bq >> upsert_to_bq

            grouped_task.append(table_group)

        check_dataset_task >> create_dataset_task
        create_dataset_task >> [task for task in grouped_task]
    
    return dag

globals()["library_postgres_db_to_bigquery"] = create_dag()
