import pandas as pd
import psycopg2


async def fetch_data_from_database(db: str):
    db_connection = psycopg2.connect(
        host="localhost",
        port="5432",
        user="postgres",
        password="admin",
        database="model_data"
    )

    sql_query = f"SELECT * FROM {db}"
    df = pd.read_sql(sql_query, db_connection)

    # Close the database connection
    db_connection.close()

    # Perform data analysis or manipulation with Pandas
    return df  # Display the first few rows of the DataFrame
