from airflow import DAG
from datetime import datetime
from airflow.operators.python import PythonOperator
from helper.postgres_app_helper import quick_command

def ensure_table():
    ensure_table_query = """
    CREATE TABLE IF NOT EXISTS users_salary (
        ID VARCHAR(50),
        NAME VARCHAR(50),
        AGE INT,
        JOB VARCHAR(50),
        INDUSTRY VARCHAR(50),
        SALARY DOUBLE PRECISION,
        INPUT_TIME TIMESTAMP    
    );
"""
    quick_command(ensure_table_query, "application_postgres", "5432", "application_db", "library_admin", "letsreadbook")

with DAG('generate_table_dag',
         start_date=datetime(2024, 12, 11),
         tags=['app_dag'],
         schedule='@hourly',
         catchup=False) as dag:
    
    create_table = PythonOperator(task_id='create_tables', python_callable=ensure_table)