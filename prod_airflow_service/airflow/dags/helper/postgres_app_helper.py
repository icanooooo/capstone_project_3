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

def ensure_table():
    ensure_table_query = """
    CREATE TABLE IF NOT EXISTS author_table (
        id INTEGER PRIMARY KEY,
        name VARCHAR(50),
        date_of_birth TIMESTAMP,
        input_date TIMESTAMP
    );
"""
    quick_command(ensure_table_query, "application_postgres", "5432", "application_db", "library_admin", "letsreadbook")

    ensure_table_query = """
    CREATE TABLE IF NOT EXISTS books_table (
        id INTEGER PRIMARY KEY,
        name VARCHAR(50),
        CONSTRAINT author_id FOREIGN KEY (id) REFERENCES author_table(id),
        genre VARCHAR(50),
        release_date TIMESTAMP,
        stock INTEGER,
        input_date TIMESTAMP
    );
"""
    quick_command(ensure_table_query, "application_postgres", "5432", "application_db", "library_admin", "letsreadbook")

    ensure_table_query = """
    CREATE TABLE IF NOT EXISTS library_member (
        id INTEGER PRIMARY KEY,
        name VARCHAR(50),
        age int,
        input_date TIMESTAMP
    );
"""
    quick_command(ensure_table_query, "application_postgres", "5432", "application_db", "library_admin", "letsreadbook")

    ensure_table_query = """
    CREATE TABLE IF NOT EXISTS rent_table (
        id INTEGER PRIMARY KEY,
        CONSTRAINT book_id FOREIGN KEY (id) REFERENCES books_table(id),  
        CONSTRAINT library_member_id FOREIGN KEY (id) REFERENCES library_member(id),
        rent_date TIMESTAMP,
        return_date TIMESTAMP,
        input_date TIMESTAMP
    );
"""
    quick_command(ensure_table_query, "application_postgres", "5432", "application_db", "library_admin", "letsreadbook")
