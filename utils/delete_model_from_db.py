import pandas as pd
import psycopg2


def delete_model_from_db(model_name):
    db_connection = psycopg2.connect(
        host="localhost",
        port="5432",
        user="postgres",
        password="admin",
        database="ai_nexus"
    )
    
    cursor = db_connection.cursor()
    sql_statement = "DELETE FROM models WHERE model_name=%s "
    cursor.execute(sql_statement,(model_name,))
    db_connection.commit()
    cursor.close()
    db_connection.close()