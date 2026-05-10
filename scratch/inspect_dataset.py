import pandas as pd
import sys

try:
    file_path = r'c:\Users\chakr\Desktop\fact-checking-main\master_dataset_sante_multilingueV1.xls'
    # Try reading with xlrd (for .xls)
    try:
        df = pd.read_excel(file_path, engine='xlrd')
    except:
        # Fallback to default/openpyxl if it's actually an xlsx renamed
        df = pd.read_excel(file_path)
    
    print("--- HEADERS ---")
    print(df.columns.tolist())
    print("\n--- FIRST 5 ROWS ---")
    print(df.head(5).to_string())
    print("\n--- INFO ---")
    print(df.info())
    print("\n--- MISSING VALUES ---")
    print(df.isnull().sum())
except Exception as e:
    print(f"ERROR: {e}")
