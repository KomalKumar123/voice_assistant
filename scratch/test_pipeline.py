import os
import sys
import json
import pandas as pd
from dataclasses import asdict

# Add project root to sys.path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data.excel_loader import ExcelLoader
from data.dataframe_store import DataFrameStore
from metadata.road_registry import RoadRegistry
from agent.road_agent import RoadAgent


def generate_mock_excel(file_path: str, road_name: str):
    """
    Generates a mock Excel file with two sheets containing highway condition data.
    """
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    
    # Adjust mock values slightly between roads to test comparative logic
    pothole_base = 0 if road_name == "Road_A" else 2
    rut_base = 0.0 if road_name == "Road_A" else 2.5
    
    # Sheet 1: Jul-24 Comparison
    jul_data = {
        "Chainage": [1000, 1100, 1200, 1300, 1400],
        "Lane": ["L1", "L2", "L1", "L2", "L1"],
        "Rut Depth": [10.5 + rut_base, 15.2 + rut_base, 8.4 + rut_base, 12.1 + rut_base, 9.3 + rut_base],
        "Potholes": [2 + pothole_base, 0 + pothole_base, 5 + pothole_base, 1 + pothole_base, 0 + pothole_base],
        "Cracking": [5.2, 12.0, 1.5, 8.4, 3.1],
        "BI": [2200, 3100, 1800, 2500, 2100]
    }
    df_jul = pd.DataFrame(jul_data)
    
    # Sheet 2: Mar-25 Comparison
    mar_data = {
        "Chainage": [1000, 1100, 1200, 1300, 1400],
        "Lane": ["L1", "L2", "L1", "L2", "L1"],
        "Rut Depth": [12.1 + rut_base, 16.5 + rut_base, 9.1 + rut_base, 13.8 + rut_base, 10.2 + rut_base],
        "Potholes": [1 + pothole_base, 3 + pothole_base, 2 + pothole_base, 0 + pothole_base, 1 + pothole_base],
        "Cracking": [6.1, 14.5, 2.0, 9.1, 4.0],
        "BI": [2400, 3300, 1950, 2700, 2300]
    }
    df_mar = pd.DataFrame(mar_data)
    
    # Write to Excel
    with pd.ExcelWriter(file_path, engine="openpyxl") as writer:
        df_jul.to_excel(writer, sheet_name="Jul-24 Comparison with CA @100m", index=False)
        df_mar.to_excel(writer, sheet_name="Mar-25 Comparison with CA @100m", index=False)
        
    print(f"Mock Excel data generated for {road_name} at: {file_path}")


def run_pipeline_test():
    scratch_dir = os.path.dirname(os.path.abspath(__file__))
    file_a = os.path.join(scratch_dir, "Road_A.xlsx")
    file_b = os.path.join(scratch_dir, "Road_B.xlsx")
    
    # 1. Generate mockup Excel files
    generate_mock_excel(file_a, "Road_A")
    generate_mock_excel(file_b, "Road_B")
    
    # 2. Load Excel files and register them
    print("\n--- Loading and Registering Excel Data ---")
    for file_path, name, dataset_id in [(file_a, "Road_A", "dataset_1"), (file_b, "Road_B", "dataset_2")]:
        sheets, metadata = ExcelLoader.load_excel(file_path)
        
        # Store data in DataFrameStore
        DataFrameStore.add_dataset(dataset_id, name, sheets, metadata)
        
        # Register dataset metadata in RoadRegistry
        available_sheets = list(sheets.keys())
        RoadRegistry.register_dataset(dataset_id, name, file_path, available_sheets)
        
    print(f"Registered Datasets: {DataFrameStore.get_dataset_names()}")
    
    # 3. Initialize Agent
    print("\n--- Initializing Road Agent ---")
    try:
        agent = RoadAgent()
    except Exception as e:
        print(f"Failed to initialize RoadAgent: {str(e)}")
        print("Please make sure the configured LLM provider is running/accessible and has the model loaded.")
        return
        
    # 4. Define test queries
    test_questions = [
        "Which chainage has the maximum rut depth in Road_A?",
        "Compare Road_A and Road_B for worst potholes.",
        "Compare the average Roughness Index (BI) of Road_A between Jul-24 and Mar-25."
    ]
    
    # 5. Run queries
    dataset_store = DataFrameStore.get_dataset_store()
    metadata_store = DataFrameStore.get_metadata()
    
    for i, q in enumerate(test_questions, 1):
        print(f"\n========================================")
        print(f"Test Question {i}: {q}")
        print(f"========================================")
        
        # Run agent
        response = agent.answer(q, dataset_store, metadata_store)
        
        print("\n[Parsed RoadQuery Object]:")
        print(json.dumps(asdict(response["road_query"]), indent=2))
        print("\n[Generated Python Code]:")
        print(response["generated_code"])
        print("\n[Raw Calculation Result]:")
        print(response["raw_result"])
        print("\n[Voice Response Narrated]:")
        print(response["final_answer"])
        print(f"========================================\n")


if __name__ == "__main__":
    run_pipeline_test()
