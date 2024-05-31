import pandas as pd
import psycopg2
import uuid

def generate_and_store_key(user_email):
    db_connection = psycopg2.connect(
        host="localhost",
        port="5432",
        user="postgres",
        password="admin",
        database="ai_nexus"
    )

    uuid4 = str(uuid.uuid4())
    cursor = db_connection.cursor()
    sql_statement = "INSERT INTO api_key VALUES(%s,%s)"
    cursor.execute(sql_statement,(user_email,uuid4))
    db_connection.commit()
    cursor.close()
    db_connection.close()

    return uuid4