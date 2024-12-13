from airflow import DAG
from datetime import datetime
from airflow.operators.python import PythonOperator
from helper.postgres_app_helper import ensure_table, get_data_id_list, insert_data
from helper.generate_data import generate_all_data

def generate_data():
    ensure_table()

    rent_result, book_result, member_result = get_data_id_list()

    book_data, member_data, rent_data = generate_all_data(book_result, member_result, rent_result)

    return {'book_data': book_data, 'member_data': member_data, 'rent_data': rent_data}

def insert_data_to_postges(**kwargs):
    ti = kwargs['ti']
    result = ti.xcom_pull(task_ids='generate_data')

    for i in result['rent_data']:
        if isinstance(i['book_id'], int):
            print(i['book_id'], ' is an integer')
        else:
            i['book_id'] = i['book_id'][0]
            i['library_member_id'] = i['library_member_id'][0]

    print(result)
    insert_data(result['book_data'], result['member_data'], result['rent_data'])
    

with DAG('generate_data_dag',
         start_date=datetime(2024, 12, 11),
         tags=['app_dag'],
         schedule='@hourly',
         catchup=False) as dag:
    
    generateData = PythonOperator(task_id='generate_data', python_callable=generate_data)
    insert_to_postgres = PythonOperator(task_id='insert_to_postgres', python_callable=insert_data_to_postges)

    generateData >> insert_to_postgres