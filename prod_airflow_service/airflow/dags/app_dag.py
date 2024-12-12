from airflow import DAG
from datetime import datetime
from airflow.operators.python import PythonOperator
from helper.postgres_app_helper import ensure_table

def generate_data():
    ensure_table()


with DAG('generate_table_dag',
         start_date=datetime(2024, 12, 11),
         tags=['app_dag'],
         schedule='@hourly',
         catchup=False) as dag:
    
    create_table = PythonOperator(task_id='create_tables', python_callable=generate_data)