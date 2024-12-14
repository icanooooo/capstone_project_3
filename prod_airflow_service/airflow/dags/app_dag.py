from airflow import DAG
from datetime import datetime
from airflow.operators.python import PythonOperator
from airflow.utils.task_group import TaskGroup
from helper.postgres_app_helper import ensure_table, get_data_id_list, insert_data, insert_book_data, insert_member_data
from helper.generate_data import generate_all_data, generate_book_data, generate_member_data

# def generate_data():
#     ensure_table()

#     rent_result, book_result, member_result = get_data_id_list()

#     book_data, member_data, rent_data = generate_all_data(book_result, member_result, rent_result)

#     return {'book_data': book_data, 'member_data': member_data, 'rent_data': rent_data}

# def insert_data_to_postges(**kwargs):
#     ti = kwargs['ti']
#     result = ti.xcom_pull(task_ids='generate_data')

#     for i in result['rent_data']:
#         if isinstance(i['book_id'], int):
#             print(i['book_id'], ' is an integer')
#         else:
#             i['book_id'] = i['book_id'][0]
#             i['library_member_id'] = i['library_member_id'][0]

#     print(result)
#     insert_data(result['book_data'], result['member_data'], result['rent_data'])

def generate_id_list():
    ensure_table()

    rent_result, book_result, member_result = get_data_id_list()

    return {'book_id_list': book_result, 'member_id_list': member_result, 'rent_id_list': rent_result}

def generate_books(**kwargs):
    ti = kwargs['ti']
    book_id_list = ti.xcom_pull(task_ids='generate_id')['book_id_list']

    if book_id_list is None:
        book_id_list = []
    
    book_data = generate_book_data(len(book_id_list))

    return book_data

def insert_books(**kwargs):
    ti = kwargs['ti']
    book_data = ti.xcom_pull(task_ids='Books.generate_book_data')

    insert_book_data(book_data)

def generate_member(**kwargs):
    ti = kwargs['ti']
    member_id_list = ti.xcom_pull(task_ids='generate_id')['member_id_list'] # return dari sini adalah list

    if member_id_list is None:
        member_id_list = []

    member_data = generate_member_data(len(member_id_list))

    return member_data

def insert_member(**kwargs):
    ti = kwargs['ti']
    member_data = ti.xcom_pull(task_ids='Members.generate_member_data')

    insert_member_data(member_data)


with DAG('generate_data_dag',
         start_date=datetime(2024, 12, 14),
         tags=['app_dag'],
         schedule='@once',
         catchup=False) as dag:

    generateIdList = PythonOperator(task_id='generate_id', python_callable=generate_id_list)

    with TaskGroup("Books") as book_data:
        generateBookData = PythonOperator(task_id='generate_book_data', python_callable=generate_books)
        insertBookData = PythonOperator(task_id='insert_book_data', python_callable=insert_books)

        generateBookData >> insertBookData

    with TaskGroup("Members") as member_data:
        generateMemberData = PythonOperator(task_id='generate_member_data', python_callable=generate_member)
        insertMemberData = PythonOperator(task_id='insert_member_data', python_callable=insert_member)

        generateMemberData >> insertMemberData

    generateIdList >> [book_data, member_data]

    # generateData = PythonOperator(task_id='generate_data', python_callable=generate_data)
    # insert_to_postgres = PythonOperator(task_id='insert_to_postgres', python_callable=insert_data_to_postges)

    # generateData >> insert_to_postgres