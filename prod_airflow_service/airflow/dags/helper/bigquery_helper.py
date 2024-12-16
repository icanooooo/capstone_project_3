from google.cloud import bigquery
from google.auth import default
import pandas as pd

#Creating client
def create_client():
    scopes=["https://www.googleapis.com/auth/cloud-platform"]

    credentials, _ = default(scopes=scopes)

    client = bigquery.Client(credentials=credentials)

    return client

#reading data from bigquery
def read_bigquery(client, what_to_query):
    df = client.query(what_to_query).result().to_dataframe()

    return df

# Function to help to create schema based on pandas column datatype
def create_schema(dataframe):
    schema = []
    for col in dataframe.columns:
        dtype = dataframe[col].dtype

        if pd.api.types.is_integer_dtype(dtype):
            field_type = "INT64"
        elif pd.api.types.is_float_dtype(dtype):
            field_type = "FLOAT64"
        elif pd.api.types.is_datetime64_any_dtype(dtype):
            field_type = "TIMESTAMP"         

        mode = "REQUIRED" if dataframe[col].notna().all() else "NULLABLE"

        if pd.api.types.is_object_dtype(dtype):
            field_type = "STRING"

            mode = "NULLABLE"

        schema.append(bigquery.SchemaField(col, field_type, mode=mode))

    return schema


# Creating table
def create_table(client, table_id, schema, partition_col=None):
    try:
        table = bigquery.Table(table_ref=table_id, schema=schema)

        if partition_col:
            table.time_partitioning = bigquery.TimePartitioning(
                type_=bigquery.TimePartitioningType.DAY,
                field=partition_col
            )            

        client.create_table(table)
        print("Loaded table to bigQuery! ")
    except Exception as e:
        print(f"Error: {e}")
        client.get_table(table_id)



# Loading data to bigQuery
def load_bigquery(client, dataframe, table_id, mode, partition_field=None):
    # Akan print table already exist jika ada
    create_table(client, table_id, create_schema(dataframe), partition_field)

    job_config = bigquery.LoadJobConfig(
        schema = create_schema(dataframe),
        write_disposition=mode,
    )

    if partition_field:
        job_config.time_partitioning = bigquery.TimePartitioning(
            field=partition_field
        )

    job = client.load_table_from_dataframe(
        dataframe, table_id, job_config=job_config
    )
    job.result()

# functions to drop table
def drop_table(client, table_id):
    client.delete_table(table_id, not_found_ok=True)

    print(f"Deleted table `{table_id}`.")