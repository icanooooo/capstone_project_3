import requests
import random
import pytz

from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

local_tz = pytz.timezone('Asia/Jakarta')

def generate_name():
    response = requests.get('https://randomuser.me/api/?nat=AU')

    if response.status_code == 200:
        user_data = response.json()['results'][0]
        full_name = f"{user_data['name']['first']} {user_data['name']['last']}"

        return full_name
    
    else:
        return f"error: {response.text}"

def generate_member_data(last_id_number): #Menerima hanya int
    data = []

    for i in range(20):
        user_data = {}
        user_data['id'] = last_id_number + 1 + i
        user_data['name'] = generate_name()
        user_data['age'] = random.randint(15, 35)
        user_data['input_time'] = datetime.now(ZoneInfo('Asia/Jakarta')).strftime('%Y-%m-%d %H:%M:%S')
    
        data.append(user_data)

    return data

def generate_book_data(last_id_number): # Hanya menerima int
    response = requests.get('https://openlibrary.org/subjects/english.json?limit=200')

    if response.status_code == 200:
        all_books = []

        for i in range (25):
            response_data = response.json()["works"][i+last_id_number]

            data = {}

            data['id'] = last_id_number + i + 1
            data['title'] = response_data['title']
            data['author_name'] = response_data['authors'][0]['name']
            data['genre'] = response_data['subject'][0:3]
            data['release_year'] = response_data['first_publish_year']
            data['stock'] = random.randint(10, 20)
            data['input_time'] = datetime.now(ZoneInfo('Asia/Jakarta')).strftime('%Y-%m-%d %H:%M:%S')

            all_books.append(data)

        return all_books

    else:
        return f"Error: {response.text}"
    
def generate_rent_data(book_id_list, member_id_list, last_id_number):
    rend_data = []
    
    for i in range(10):
        data = {}

        rent_day = datetime.now(ZoneInfo('Asia/Jakarta')) - timedelta(random.randint(2,4))
        return_day = datetime.now(ZoneInfo('Asia/Jakarta')) + timedelta(random.randint(2,4))

        data['id'] = len(last_id_number) + i + 1
        data['book_id'] = random.choice(book_id_list)
        data['library_member_id'] = random.choice(member_id_list)
        data['rent_date'] = rent_day.strftime('%Y-%m-%d %H:%M:%S')
        data['return_date'] = return_day.strftime('%Y-%m-%d %H:%M:%S')
        data['input_time'] = datetime.now(ZoneInfo('Asia/Jakarta')).strftime('%Y-%m-%d %H:%M:%S')


        rend_data.append(data)

    return rend_data

def generate_all_data(book_id_list, member_id_list, rent_id_list):
    book_data = generate_book_data(len(book_id_list))
    member_data = generate_member_data(len(member_id_list))
    
    if len(book_id_list) == 0:
        book_id_list = []
        for i in book_data:
            book_id_list.append(i['id'])

    if len(member_id_list) == 0:
        member_id_list = []
        for i in member_data:
            member_id_list.append(i['id'])

    print(book_id_list)

    rent_data = generate_rent_data(book_id_list, member_id_list, len(rent_id_list))

    return book_data, member_data, rent_data
