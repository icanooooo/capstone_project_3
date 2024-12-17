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

def get_last_updated(client, table_id):
    query = f"""
        SELECT MAX(created_at) AS last_updated
        FROM `{table_id}`
    """

    query_job = client.query(query)
    result = query_job.result()

    last_updated_timestamp = None
    for row in result:
        last_updated_timestamp = row['last_updated']

    if not last_updated_timestamp:
        last_updated_timestamp = "1970-01-01 00:00:00" # for firsttime ingestion

    return last_updated_timestamp

def incremental_load(client, dataframe, table_id, mode, partition_field=None):
    # Akan print table already exist jika ada
    create_table(client, table_id, create_schema(dataframe), partition_field)

    last_updated_timestamp = get_last_updated(client, table_id)

    incremental_df = dataframe[dataframe['created_at'] > last_updated_timestamp]

    job_config = bigquery.LoadJobConfig(
        schema = create_schema(incremental_df),
        write_disposition=mode,
    )

    if partition_field:
        job_config.time_partitioning = bigquery.TimePartitioning(
            field=partition_field
        )

    job = client.load_table_from_dataframe(
        incremental_df, table_id, job_config=job_config
    )
    job.result()

def get_schema(client, table_id):
    table = client.get_table(table_id)
    schema = [field.name for field in table.schema]

    return schema

def upsert_data(client, stage_id, table_id, unique_key, dataframe, partition_field):
    try:
        create_table(client, table_id, create_schema(dataframe), partition_field)
    except:
        print("table already exist")

    columns = get_schema(client, table_id)
    columns.remove(unique_key)

    update_set = ", ".join([f"prod.{col} = stage.{col}" for col in columns])
    
    insert_columns = ", ".join([unique_key] + columns)
    insert_values = ", ".join([f"stage.{col}" for col in [unique_key] + columns])

    merge_query = f"""
    MERGE `{table_id}` prod
    USING `{stage_id}` stage
    ON prod.{unique_key} = stage.{unique_key}
    WHEN MATCHED THEN
        UPDATE SET {update_set}
    WHEN NOT MATCHED THEN
        INSERT ({insert_columns})
        VALUES ({insert_values})
"""

    print(f"Merging with {stage_id} with {table_id}...")
    query_job = client.query(merge_query)
    query_job.result()
    print("Merge succesful!")