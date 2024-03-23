import pandas as pd
import psycopg2


def save_logs_for_user(user_email, date ,logs):
    db_connection = psycopg2.connect(
        host="localhost",
        port="5432",
        user="postgres",
        password="admin",
        database="ai_nexus"
    )
    cursor = db_connection.cursor()
    sql_statement = "INSERT INTO logs VALUES(%s,%s, %s)"
    cursor.execute(sql_statement,(user_email,date, logs))
    db_connection.commit()
    cursor.close()
    db_connection.close()