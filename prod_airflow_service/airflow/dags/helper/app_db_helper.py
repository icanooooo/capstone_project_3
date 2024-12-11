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
    quick_command(ensure_table_query, "localhost", "5432", "application_db", "library_admin", "letsreadbook")