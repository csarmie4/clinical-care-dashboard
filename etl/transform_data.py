import pandas as pd
import os
import sys
import numpy as np

RAW_CSV_PATH = os.getenv("RAW_CSV_PATH")
if not RAW_CSV_PATH:
    sys.exit("Error: RAW_CSV_PATH environment variable not set.")

files = [
    "patients.csv", "observations.csv", "careplans.csv", "conditions.csv", 
    "encounters.csv", "immunizations.csv", "medications.csv", "procedures.csv"
]

dataframes = {}
for file in files:
    file_path = os.path.join(RAW_CSV_PATH, file)
    try:
        df = pd.read_csv(file_path)
        df.replace({'NaN': np.nan, 'nan': np.nan}, inplace=True)
        dataframes[file.split(".")[0]] = df
        print(f"Successfully loaded {file}")
    except Exception as e:
        print(f"Failed to load {file}: {e}")

def standardize_column_names(df):
    df.columns = df.columns.str.strip().str.upper().str.replace(" ", "_")
    return df

def fix_data_types_simple(df):
    categorical_cols = {'MARITAL', 'RACE', 'ETHNICITY', 'GENDER', 'STATE', 'COUNTY', 
                        'CATEGORY', 'TYPE', 'ENCOUNTERCLASS', 'DESCRIPTION'}
    id_cols = {'ID', 'PATIENT', 'ENCOUNTER'}

    for col in df.columns:
        if any(kw in col.lower() for kw in ['date', 'start', 'stop']):
            df[col] = pd.to_datetime(df[col], errors='coerce', utc=True)
        if col in categorical_cols:
            unique_vals = df[col].nunique()
            df[col] = df[col].astype('category') if unique_vals < 100 else df[col].astype(str)
        if col in id_cols or df[col].dtype == 'object':
            df[col] = df[col].astype(str)
        if df[col].dtype == 'int64':
            df[col] = df[col].astype('Int64')
    return df

def drop_columns_if_exists(df, columns):
    to_drop = [col for col in columns if col in df.columns]
    if to_drop:
        print(f"Dropping columns: {to_drop}")
        df.drop(columns=to_drop, inplace=True)
    return df

drop_cols = ['SSN', 'DRIVERS', 'PASSPORT', 'FIRST', 'MIDDLE', 'LAST', 'MAIDEN',
             'PREFIX', 'SUFFIX', 'ADDRESS', 'BIRTHPLACE', 'FIPS']

cleaning_funcs = {
    "patients": lambda df: drop_columns_if_exists(df, drop_cols),
    "conditions": lambda df: drop_columns_if_exists(df, ["SYSTEM"]),
    "immunizations": lambda df: drop_columns_if_exists(df, ["BASE_COST"]),
    "procedures": lambda df: drop_columns_if_exists(df, ["SYSTEM"]),
}

def clean_csv_data():
    cleaned = {}
    for name, df in dataframes.items():
        df = standardize_column_names(df)
        df = fix_data_types_simple(df)
        df = cleaning_funcs.get(name, lambda x: x)(df)
        cleaned[name] = df

        print(f"DataFrame: {name}")
        print("Columns and Data Types:")
        print(df.dtypes)
        print("-" * 50)
    
    return cleaned

