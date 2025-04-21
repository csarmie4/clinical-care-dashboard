import os
import sys
import snowflake.connector
from transform_data import clean_csv_data
from snowflake.connector.pandas_tools import write_pandas


# =========================
# Snowflake Connection
# =========================
def get_snowflake_connection():
    try:
        conn = snowflake.connector.connect(
            user=os.getenv("SNOWFLAKE_USER"),
            password=os.getenv("SNOWFLAKE_PASSWORD"),
            account=os.getenv("SNOWFLAKE_ACCOUNT"),
            warehouse=os.getenv("SNOWFLAKE_WAREHOUSE"),
            database=os.getenv("SNOWFLAKE_DATABASE"),
            schema=os.getenv("SNOWFLAKE_SCHEMA_STAGING"),
            role=os.getenv("SNOWFLAKE_ROLE")
        )
        return conn
    except Exception as e:
        print("Error connecting to Snowflake:", e)
        sys.exit(1)

# =========================
# Load DataFrames to Snowflake
# =========================
def load_dataframe_to_snowflake(df, table_name, conn):
    try:
        # Write DataFrame to Snowflake using write_pandas
        success, nchunks, nrows, _ = write_pandas(
            conn=conn,
            df=df,
            table_name=table_name.upper(),  # Snowflake prefers uppercase
            schema=os.getenv("SNOWFLAKE_SCHEMA_STAGING"),
            overwrite=True,  # Replace table contents if it exists
            use_logical_type=True
        )

        if success:
            print(f"Loaded '{table_name}' to Snowflake — {nrows} rows.")
        else:
            print(f"Partial load of '{table_name}' — check logs.")
    except Exception as e:
        print(f"Failed to load '{table_name}' to Snowflake:", e)

# =========================
# Main ETL Task
# =========================
def load_staging_data():
    print("========== STARTING FULL ETL PIPELINE ==========")

    # Step 1: Clean data using transform script
    cleaned_dataframes = clean_csv_data()

    # Step 2: Connect to Snowflake
    conn = get_snowflake_connection()

    # Step 3: Upload each DataFrame
    print("[STEP 2 & 3] Transforming data and loading into STAGING schema...")
    for table_name, df in cleaned_dataframes.items():
        load_dataframe_to_snowflake(df, table_name, conn)

    # Step 4: Close connection
    conn.close()
    print("========== ETL PIPELINE COMPLETE  ==========")
