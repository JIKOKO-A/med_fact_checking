import pandas as pd

file_path = r'c:\Users\chakr\Desktop\fact-checking-main\master_dataset_sante_multilingueV1.xls'

# Read as CSV since it's actually CSV
df = pd.read_csv(file_path)

print("--- LABEL DISTRIBUTION ---")
print(df['label'].value_counts())

print("\n--- LANGUAGE DISTRIBUTION ---")
print(df['langue'].value_counts())

# Check for duplicates
duplicates = df.duplicated().sum()
print(f"\n--- DUPLICATES: {duplicates} ---")

# Check for empty entries
empty_text = df['text'].isna().sum()
print(f"--- EMPTY TEXT ENTRIES: {empty_text} ---")
