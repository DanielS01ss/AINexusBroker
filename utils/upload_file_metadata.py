import pandas as pd
import psycopg2
from psycopg2 import Error
from datetime import datetime
from utils.fetch_all_datasets import fetch_data_from_database
from utils.remove_csv_extension import remove_csv_extension

async def upload_file_metadata(user_email, file_name, tags, authors, publish, description):
    try:
        db_connection = psycopg2.connect(
            host="localhost",
            port="5432",
            user="postgres",
            password="admin",
            database="model_data"
        )

        df = await fetch_data_from_database()
        last_id = df.tail(1)['dataset_id'].iloc[0]
        last_id = int(last_id)
        cursor = db_connection.cursor()
        sql_statement = f"INSERT INTO all_datasets (id, dataset_name, dataset_id, dataset_info_id, database_name, database_type) VALUES(%s, %s, %s, %s, %s, %s)"
        cursor.execute(sql_statement,(last_id+1, remove_csv_extension(file_name),last_id+1,last_id+1,file_name,user_email))
        db_connection.commit()
        
        parsed_tags = "{" + ", ".join(tags) + "}"
        parsed_authors = "{" + ", ".join(authors) + "}"

        sql_statement = f"INSERT INTO dataset_info (id, about, keywords, authors, publish, datasetid, user_name) VALUES(%s, %s, %s, %s, %s, %s, %s)"
        cursor.execute(sql_statement,(last_id+1, description, parsed_tags, parsed_authors, publish, last_id+1, user_email))
        db_connection.commit()



    except Error as e:
        print(f"There was an error while inserting data into the database:{e}")
    finally:
        if db_connection:
            cursor.close()
            db_connection.close()
            print("The database connection was successfully closed!")    

