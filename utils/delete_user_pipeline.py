import pandas as pd
import psycopg2

def delete_user_pipeline(pipeline_name):
    print("The pipeline name is:")
    print(pipeline_name)
    db_connection = psycopg2.connect(
        host="localhost",
        port="5432",
        user="postgres",
        password="admin",
        database="ai_nexus"
    )
    
    cursor = db_connection.cursor()
    sql_statement = "DELETE FROM pipeline_save WHERE pipeline_name=%s "
    cursor.execute(sql_statement,(pipeline_name,))
    db_connection.commit()
    cursor.close()
    db_connection.close()