import pandas as pd
import psycopg2
from minio import Minio, S3Error


def delete_dataset_after_id(dataset_id):
    db_connection = psycopg2.connect(
        host="localhost",
        port="5432",
        user="postgres",
        password="admin",
        database="model_data"
    )

    sql_query = f"SELECT * FROM all_datasets"
    df = pd.read_sql(sql_query, db_connection)


    entry = df.loc[df["id"] == dataset_id]
    entry_value = entry["database_name"].values[0]
    
    cursor = db_connection.cursor()
    sql_statement = "DELETE FROM all_datasets WHERE id=%s "
    cursor.execute(sql_statement,(dataset_id,))
    db_connection.commit()
    cursor.close()

    cursor = db_connection.cursor()
    sql_statement = "DELETE FROM dataset_info WHERE id=%s "
    cursor.execute(sql_statement,(dataset_id,))
    db_connection.commit()
    cursor.close()


    #stergere din MINIO
    db_connection.close()


    minio_client = Minio(
            "127.0.0.1:9000",
            access_key="LjYOcfvfYyfYPg0ea3D3",
            secret_key="QKd4F1cgxMTLAh2MFtHYTWePbrurXNeMlf13h06D",
            secure=False  # Set to True if using HTTPS
    )


    try:
        minio_client.remove_object("datasets", entry_value)
        print(f"File '{entry_value}' deleted successfully from bucket 'ainexusmetrics'.")
    except S3Error as e:
        print(f"Failed to delete file '{entry_value}' from bucket 'ainexusmetrics': {e}")
    
    # Perform data analysis or manipulation with Pandas
    return df  # Display the first few rows of the DataFrame