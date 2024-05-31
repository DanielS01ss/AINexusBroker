import pandas as pd
import psycopg2


async def fetch_generated_key(email: str):
    db_connection = psycopg2.connect(
        host="localhost",
        port="5432",
        user="postgres",
        password="admin",
        database="ai_nexus"
    )

    cursor = db_connection.cursor()
    sql_statement = f"SELECT * FROM api_key WHERE username=\'{email}\'"
    cursor.execute(sql_statement,(email))
    results = cursor.fetchall()


    return results