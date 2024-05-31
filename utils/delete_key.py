import pandas as pd
import psycopg2


def delete_key_for_user(key):
    db_connection = psycopg2.connect(
        host="localhost",
        port="5432",
        user="postgres",
        password="admin",
        database="ai_nexus"
    )
    
    cursor = db_connection.cursor()
    sql_statement = "DELETE FROM api_key WHERE key=%s "
    cursor.execute(sql_statement,(key,))
    db_connection.commit()
    cursor.close()
    db_connection.close()