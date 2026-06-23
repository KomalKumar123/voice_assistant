import os
import pandas as pd


class ExcelLoader:

    @staticmethod
    def load_excel(file_path: str) -> tuple[dict[str, pd.DataFrame], dict]:
        """
        Loads all sheets of an Excel file into Pandas DataFrames and
        generates schema metadata.
        
        Returns:
            dfs (dict): Dictionary mapping sheet names to DataFrames.
            metadata (dict): Metadata including columns, shapes, and types.
        """
        if not os.path.exists(file_path):
            return {}, {}
            
        excel_file = pd.ExcelFile(file_path)
        dfs = {}
        metadata = {}
        
        for sheet in excel_file.sheet_names:
            df = pd.read_excel(file_path, sheet_name=sheet)
            dfs[sheet] = df
            
            # Extract column info and shape
            metadata[sheet] = {
                "columns": list(df.columns),
                "shape": df.shape,
                "dtypes": {str(col): str(dtype) for col, dtype in df.dtypes.items()}
            }
            
        return dfs, metadata
