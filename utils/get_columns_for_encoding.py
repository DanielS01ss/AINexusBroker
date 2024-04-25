import pandas as pd


def get_columns_for_encoding(df):
    valid_columns = []
    for column in df.columns:
        if df[column].nunique() <= 10:
            valid_columns.append(column)
    return valid_columns