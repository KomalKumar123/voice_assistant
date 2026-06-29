import sys
import time
import pandas as pd

file_path = "d:/Projects/Voice_assist/scratch/mock_road_data.xlsx"

# Method 1: Re-reading by path (Current code)
start = time.time()
excel_file = pd.ExcelFile(file_path)
for sheet in excel_file.sheet_names:
    df = pd.read_excel(file_path, sheet_name=sheet)
print(f"Method 1 (re-reading path): {time.time() - start:.2f}s")

# Method 2: Reusing ExcelFile object via pd.read_excel
start = time.time()
excel_file = pd.ExcelFile(file_path)
for sheet in excel_file.sheet_names:
    df = pd.read_excel(excel_file, sheet_name=sheet)
print(f"Method 2 (reusing ExcelFile via read_excel): {time.time() - start:.2f}s")

# Method 3: Reusing ExcelFile object via parse
start = time.time()
excel_file = pd.ExcelFile(file_path)
for sheet in excel_file.sheet_names:
    df = excel_file.parse(sheet_name=sheet)
print(f"Method 3 (reusing ExcelFile via parse): {time.time() - start:.2f}s")

# Method 4: Reusing ExcelFile with data_only=True engine_kwargs via parse
try:
    start = time.time()
    excel_file = pd.ExcelFile(file_path, engine="openpyxl", engine_kwargs={"data_only": True})
    for sheet in excel_file.sheet_names:
        df = excel_file.parse(sheet_name=sheet)
    print(f"Method 4 (ExcelFile with data_only=True): {time.time() - start:.2f}s")
except Exception as e:
    print(f"Method 4 failed: {e}")

# Method 5: Calamine Engine
try:
    start = time.time()
    excel_file = pd.ExcelFile(file_path, engine="calamine")
    for sheet in excel_file.sheet_names:
        df = excel_file.parse(sheet_name=sheet)
    print(f"Method 5 (ExcelFile with calamine engine): {time.time() - start:.2f}s")
except Exception as e:
    print(f"Method 5 failed: {e}")

