import pandas as pd
import psycopg2


def delete_logs_for_user(user_email):
    db_connection = psycopg2.connect(
        host="localhost",
        port="5432",
        user="postgres",
        password="admin",
        database="ai_nexus"
    )
    
    cursor = db_connection.cursor()
    sql_statement = "DELETE FROM logs WHERE email=%s "
    cursor.execute(sql_statement,(user_email,))
    db_connection.commit()
    cursor.close()
    db_connection.close()