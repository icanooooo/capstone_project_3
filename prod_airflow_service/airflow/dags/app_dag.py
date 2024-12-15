from airflow import DAG
from datetime import datetime
from airflow.operators.python import PythonOperator
from airflow.utils.task_group import TaskGroup
from helper.postgres_app_helper import ensure_table, get_data_id_list, insert_data, insert_book_data, insert_member_data, insert_rent_data
from helper.generate_data import generate_book_data, generate_member_data, generate_rent_data

def generate_id_list():
    ensure_table()

    rent_result, book_result, member_result = get_data_id_list()

    return {'book_id_list': book_result, 'member_id_list': member_result, 'rent_id_list': rent_result}

def generate_books(**kwargs):
    ti = kwargs['ti']
    book_id_list = ti.xcom_pull(task_ids='generate_id')['book_id_list'][0]

    if not book_id_list:
        book_id_list = []
    
    book_data = generate_book_data(len(book_id_list))

    return book_data

def insert_books(**kwargs):
    ti = kwargs['ti']
    book_data = ti.xcom_pull(task_ids='Books.generate_book_data')

    insert_book_data(book_data)

def generate_member(**kwargs):
    ti = kwargs['ti']
    member_id_list = ti.xcom_pull(task_ids='generate_id')['member_id_list'][0] # return dari sini adalah list

    if not member_id_list:
        member_id_list = []

    member_data = generate_member_data(len(member_id_list))

    return member_data

def insert_member(**kwargs):
    ti = kwargs['ti']
    member_data = ti.xcom_pull(task_ids='Members.generate_member_data')

    insert_member_data(member_data)

def generate_rent_transaction(**kwargs):
    ti = kwargs['ti']
    all_ids = ti.xcom_pull(task_ids='generate_id')
    book_id_list = all_ids['book_id_list'][0]
    member_id_list = all_ids['member_id_list'][0]
    rent_id_list = all_ids['rent_id_list'][0]

    if not book_id_list:
        book_data = ti.xcom_pull(task_ids='Books.generate_book_data')
        book_id_list = [book['id'] for book in book_data]
    if not member_id_list:
        member_data = ti.xcom_pull(task_ids='Members.generate_member_data')
        member_id_list = [member['id'] for member in member_data]

    rent_id_list = rent_id_list or []

    rent_data = generate_rent_data(book_id_list, member_id_list, rent_id_list)

    # ensuring ID's are interger 
    # for i in rent_data:
    #     if isinstance(i['book_id'], int) and isinstance(i['library_member_id'], int):
    #         print(i['book_id'], ' is an integer')
    #     else:
    #         i['book_id'] = i['book_id'][0]
    #         i['library_member_id'] = i['library_member_id'][0]

    return rent_data
    
def insert_rent_transaction(**kwargs):
    ti = kwargs['ti']
    rent_data = ti.xcom_pull(task_ids='RentTransactions.generate_rent_data')

    insert_rent_data(rent_data)

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

    with TaskGroup("RentTransactions") as rent_data:
        generateRentData = PythonOperator(task_id='generate_rent_data', python_callable=generate_rent_transaction)
        insertRentData = PythonOperator(task_id='insert_rent_data', python_callable=insert_rent_transaction)

        generateRentData >> insertRentData

    generateIdList >> [book_data, member_data] >> rent_data