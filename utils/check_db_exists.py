import psycopg2


def fetch_and_check_db(db_to_search: str):
    db_connection = psycopg2.connect(
        host="localhost",
        port="5432",
        user="postgres",
        password="admin",
        database="model_data"
    )
    cursor = db_connection.cursor()
    sql_statement = "SELECT * FROM all_datasets"
    cursor.execute(sql_statement)
    result = cursor.fetchall()
    for res in result:
        if res[-2] == db_to_search:
            return res

    return None

