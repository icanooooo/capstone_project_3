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