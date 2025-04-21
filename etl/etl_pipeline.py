# run_etl_pipeline.py
import sys

# Step 1: Load raw CSVs into Snowflake RAW schema
def run_load_raw_data():
    try:
        from load_raw_data import load_raw_data
        print("[STEP 1] Loading raw data into RAW schema...")
        load_raw_data()
        print("[STEP 1] Completed loading raw data.\n")
    except Exception as e:
        print("[ERROR] Failed during load_raw_data step:", e)
        sys.exit(1)

# Step 2 & 3: Clean data and load into STAGING schema
def run_transform_and_stage():
    try:
        from load_staging_data import load_staging_data
        print("[STEP 2 & 3] Transforming data and loading into STAGING schema...")
        load_staging_data()
        print("[STEP 2 & 3] Completed loading staging data.\n")
    except Exception as e:
        print("[ERROR] Failed during transform or staging step:", e)
        sys.exit(1)

if __name__ == "__main__":
    print("========== STARTING FULL ETL PIPELINE ==========")
    # run_load_raw_data()
    run_transform_and_stage()
    print("========== ETL PIPELINE COMPLETE ✅ ==========")
