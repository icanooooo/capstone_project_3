from helper.alert_helper import send_failure_to_discord
from airflow import DAG
from airflow.operators.dummy_operator import DummyOperator
from airflow.operators.python_operator import PythonOperator
from datetime import datetime, timedelta

def failure():
    raise Exception("SIMULATION OF FAILING IN LIFE")

def create_dag():
    default_args = {
        'owner' : 'ican',
        'retries' : 1,
        'retry_delay' : timedelta(minutes=1),
        'on_failure_callback' : send_failure_to_discord,
    }

    with DAG(
        "failed_test_dag",
        start_date=datetime(2025, 1, 29),
        tags=['tests'],
        default_args=default_args,
        schedule_interval='@daily',
        catchup=False) as dag:

        task1 = DummyOperator(
            task_id='task1',
        )

        task2 = PythonOperator(
            task_id='task2',
            python_callable=failure,
        )

        task1 >> task2

    return dag

dag = create_dag()