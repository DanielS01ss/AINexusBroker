from minio import Minio
import pandas as pd


def check_and_fetch_minio(dataset_name):
    minio_client = Minio(
    endpoint='127.0.0.1:9000',
    access_key='LjYOcfvfYyfYPg0ea3D3',
    secret_key='QKd4F1cgxMTLAh2MFtHYTWePbrurXNeMlf13h06D',
    secure=False  # Ajustează la True dacă folosești HTTPS
)

    # Definește numele bucket-ului și numele fișierului CSV din MinIO
    bucket_name = 'datasets'
    object_name = dataset_name

    # Descarcă fișierul CSV din MinIO
    with minio_client.get_object(bucket_name, object_name) as file_stream:
        # Creează un DataFrame Pandas din fișierul CSV
        df = pd.read_csv(file_stream)
    df.rename(columns=lambda x: x.strip().lower().replace(' ', '-'), inplace=True)
    # Afisează DataFrame-ul
    return df