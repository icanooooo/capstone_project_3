import psycopg2

def create_connection(host, port, dbname, user, password):
    conn = psycopg2.connect(
        host=host,
        port=port,
        database=dbname,
        user=user,
        password=password
    )

    return conn

def load_query(connection, query, vals=None):
    cursor = connection.cursor()

    cursor.execute(query, vals)

    cursor.close()

def print_query(connection, query):
    cursor = connection.cursor()

    cursor.execute(query)
    result = cursor.fetchall()

    cursor.close()
    return result

def quick_command(query, host, port, dbname, user, password, vals=None):
    conn = create_connection(host, port, dbname, user, password)

    load_query(conn, query, vals)

    conn.commit()
    conn.close()

def ensure_table(host="application_postgres"):
#     ensure_table_query = """
#     CREATE TABLE IF NOT EXISTS author_table (
#         id INTEGER PRIMARY KEY,
#         name VARCHAR(50),
#         date_of_birth TIMESTAMP,
#         input_date TIMESTAMP
#     );
# """
#     quick_command(ensure_table_query, "application_postgres", "5432", "application_db", "library_admin", "letsreadbook")

    ensure_table_query = """
    CREATE TABLE IF NOT EXISTS books_table (
        id INTEGER PRIMARY KEY,
        title TEXT,
        author_name TEXT,
        genre TEXT,
        release_year INT,
        stock INTEGER,
        input_time TIMESTAMP
    );
"""
    quick_command(ensure_table_query, host, "5432", "application_db", "library_admin", "letsreadbook")

    ensure_table_query = """
    CREATE TABLE IF NOT EXISTS library_member (
        id INTEGER PRIMARY KEY,
        name TEXT,
        age int,

        input_time TIMESTAMP
    );
"""
    quick_command(ensure_table_query, host, "5432", "application_db", "library_admin", "letsreadbook")

    ensure_table_query = """
    CREATE TABLE IF NOT EXISTS rent_table (
        id INTEGER PRIMARY KEY,
        book_id INTEGER,  
        library_member_id INTEGER,
        rent_date TIMESTAMP,
        return_date TIMESTAMP,
        input_time TIMESTAMP
    );
"""
    quick_command(ensure_table_query, host, "5432", "application_db", "library_admin", "letsreadbook")


def insert_book_data(book_data, host="application_postgres"):
    insert_data = """
    INSERT INTO books_table (id, title, author_name, genre, release_year, stock, input_time)
    VALUES (%s,%s,%s,%s,%s,%s,%s)
"""
    
    for data in book_data:
        quick_command(insert_data, host, "5432", "application_db", "library_admin", "letsreadbook",
                      (data['id'], data['title'], data['author_name'], data['genre'], data['release_year'], data['stock'], data['input_time']))
        
        print(f"Succesfully added: {data['title']}")

def insert_member_data(member_data, host="application_postgres"):
    insert_data = """
    INSERT INTO library_member (id, name, age, input_time)
    VALUES (%s,%s,%s,%s)
"""
    
    for data in member_data:
        quick_command(insert_data, host, "5432", "application_db", "library_admin", "letsreadbook",
                      (data['id'], data['name'], data['age'], data['input_time']))
        
        print(f"Succesfully added: {data['name']}")

def insert_rent_data(rent_data, host="application_postgres"):
    insert_data = """
    INSERT INTO rent_table (id, book_id, library_member_id, rent_date, return_date, input_time)
    VALUES (%s,%s,%s,%s,%s,%s)
"""
    
    for data in rent_data:
        quick_command(insert_data, host, "5432", "application_db", "library_admin", "letsreadbook",
                      (data['id'], data['book_id'], data['library_member_id'], data['rent_date'], data['return_date'], data['input_time']))
        
        print(f"Succesfully added rent id: {data['id']}")

def insert_data(book_data, member_data, rent_data, host="application_postgres"):
    insert_book_data(book_data, host)
    insert_member_data(member_data, host)
    insert_rent_data(rent_data, host)

def get_data_id_list(host="application_postgres"):
    conn = create_connection(host, "5432", "application_db", "library_admin", "letsreadbook")
    
    book_query = """
        SELECT DISTINCT(id) from books_table;
    """
    book_result = print_query(conn, book_query)

    member_query = """
        SELECT DISTINCT(id) from library_member;
    """

    member_result = print_query(conn, member_query)

    rent_query = """
        SELECT DISTINCT(id) from rent_table;
    """

    rent_result = print_query(conn, rent_query)

    return rent_result, book_result, member_result