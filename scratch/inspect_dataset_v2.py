import pandas as pd
import sys

file_path = r'c:\Users\chakr\Desktop\fact-checking-main\master_dataset_sante_multilingueV1.xls'

print(f"Inspecting: {file_path}")

engines = ['xlrd', 'openpyxl', 'pyxlsb', 'odf']
success = False

for engine in engines:
    try:
        print(f"Trying engine: {engine}")
        df = pd.read_excel(file_path, engine=engine)
        print(f"SUCCESS with {engine}")
        print("\n--- HEADERS ---")
        print(df.columns.tolist())
        print("\n--- FIRST 2 ROWS ---")
        print(df.head(2).to_string())
        print("\n--- INFO ---")
        print(df.info())
        success = True
        break
    except Exception as e:
        print(f"Failed with {engine}: {e}")

if not success:
    print("Could not read Excel file with any common engine.")
    # Try reading as CSV just in case
    try:
        print("Trying as CSV...")
        df = pd.read_csv(file_path)
        print("SUCCESS as CSV")
        print(df.head(2))
    except:
        print("Failed as CSV too.")
