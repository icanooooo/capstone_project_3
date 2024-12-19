import pandas as pd

def automatically_change_dtypes(dataframe):
    columns = dataframe.columns

    for col in columns:
        if col == 'created_at':
            continue

        try:
            dataframe[col] = pd.to_numeric(dataframe[col], errors='raise')
            continue
        except ValueError:
            pass

        try:
            dataframe[col] = pd.to_datetime(dataframe[col], errors='raise')
            continue
        except ValueError:
            pass

    return dataframe