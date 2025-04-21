import snowflake.connector
import os
import glob
from dotenv import load_dotenv

load_dotenv()

def load_raw_data():
    conn = snowflake.connector.connect(
        user=os.getenv("SNOWFLAKE_USER"),
        password=os.getenv("SNOWFLAKE_PASSWORD"),
        account=os.getenv("SNOWFLAKE_ACCOUNT"),
        warehouse=os.getenv("SNOWFLAKE_WAREHOUSE"),
        database=os.getenv("SNOWFLAKE_DATABASE"),
        schema=os.getenv("SNOWFLAKE_SCHEMA_RAW"),
        role=os.getenv("SNOWFLAKE_ROLE")
    )
    cursor = conn.cursor()

    data_folder = os.getenv("RAW_CSV_PATH", "./raw_data")
    schema = os.getenv("SNOWFLAKE_SCHEMA_RAW", "RAW_DATA")

    for file_path in glob.glob(os.path.join(data_folder, "*.csv")):
        file_name = os.path.basename(file_path)
        table_name = os.path.splitext(file_name)[0].upper()
        stage_name = f"@%{table_name}"

        print(f"[INFO] Processing {file_name} → {schema}.{table_name}")

        try:
            # Step 1: Upload file to stage
            put_query = f"PUT file://{os.path.abspath(file_path)} {stage_name} OVERWRITE = TRUE"
            cursor.execute(put_query)
            print(f"[INFO] Uploaded to stage {stage_name}")

            # Step 2: COPY INTO table from staged file
            copy_query = f"""
                COPY INTO "{schema}"."{table_name}"
                FROM {stage_name}
                FILE_FORMAT = (
                    TYPE = 'CSV'
                    FIELD_OPTIONALLY_ENCLOSED_BY = '"'
                    SKIP_HEADER = 1
                    NULL_IF = ('', 'NULL')
                )
                ON_ERROR = 'CONTINUE'
            """
            cursor.execute(copy_query)
            print(f"[INFO] Loaded into table {table_name} via COPY INTO")

        except Exception as e:
            print(f"[ERROR] Failed to load {file_name}: {e}")

    cursor.close()
    conn.close()
