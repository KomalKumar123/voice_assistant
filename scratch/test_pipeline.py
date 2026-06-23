import os
import sys
import pandas as pd

# Add project root to sys.path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data.excel_loader import ExcelLoader
from data.dataframe_store import DataFrameStore
from agent.road_agent import RoadAgent


def generate_mock_excel(file_path: str):
    """
    Generates a mock Excel file with two sheets containing highway condition data.
    """
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    
    # Sheet 1: Jul-24 Comparison
    jul_data = {
        "Chainage": [1000, 1100, 1200, 1300, 1400],
        "Lane": ["L1", "L2", "L1", "L2", "L1"],
        "Rut Depth": [10.5, 15.2, 8.4, 12.1, 9.3],
        "Potholes": [2, 0, 5, 1, 0],
        "Cracking": [5.2, 12.0, 1.5, 8.4, 3.1],
        "BI": [2200, 3100, 1800, 2500, 2100]
    }
    df_jul = pd.DataFrame(jul_data)
    
    # Sheet 2: Mar-25 Comparison
    mar_data = {
        "Chainage": [1000, 1100, 1200, 1300, 1400],
        "Lane": ["L1", "L2", "L1", "L2", "L1"],
        "Rut Depth": [12.1, 16.5, 9.1, 13.8, 10.2],
        "Potholes": [1, 3, 2, 0, 1],
        "Cracking": [6.1, 14.5, 2.0, 9.1, 4.0],
        "BI": [2400, 3300, 1950, 2700, 2300]
    }
    df_mar = pd.DataFrame(mar_data)
    
    # Write to Excel
    with pd.ExcelWriter(file_path, engine="openpyxl") as writer:
        df_jul.to_excel(writer, sheet_name="Jul-24 Comparison with CA @100m", index=False)
        df_mar.to_excel(writer, sheet_name="Mar-25 Comparison with CA @100m", index=False)
        
    print(f"Mock Excel data generated at: {file_path}")


def run_pipeline_test():
    mock_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "mock_road_data.xlsx")
    
    # 1. Generate mockup Excel file
    generate_mock_excel(mock_file)
    
    # 2. Load Excel sheet into memory
    print("\n--- Loading Excel Data ---")
    dfs, metadata = ExcelLoader.load_excel(mock_file)
    DataFrameStore.set_data(dfs, metadata)
    
    print(f"Loaded Sheets: {DataFrameStore.get_sheet_names()}")
    
    # 3. Initialize Agent
    print("\n--- Initializing Agent ---")
    try:
        agent = RoadAgent()
    except Exception as e:
        print(f"Failed to initialize RoadAgent: {str(e)}")
        print("Please make sure you have set GEMINI_API_KEY in a .env file.")
        return
        
    # 4. Define test queries
    test_questions = [
        "Which chainage has the biggest pothole in Jul-24?",
        "What is the maximum rut depth in Mar-25?",
        "Compare the average Roughness Index (BI) between Jul-24 and Mar-25."
    ]
    
    # 5. Run queries
    for i, q in enumerate(test_questions, 1):
        print(f"\n========================================")
        print(f"Test Question {i}: {q}")
        print(f"========================================")
        
        # Run agent
        response = agent.answer(q, dfs, metadata)
        
        print("\n[Generated Python Code]:")
        print(response["generated_code"])
        print("\n[Raw Calculation Result]:")
        print(response["raw_result"])
        print("\n[Voice Response Narrated]:")
        print(response["final_answer"])
        print(f"========================================\n")


if __name__ == "__main__":
    run_pipeline_test()
