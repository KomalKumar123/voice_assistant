import os
import pandas as pd


class ExcelLoader:

    @staticmethod
    def load_excel(file_path: str) -> tuple[dict[str, pd.DataFrame], dict]:
        """
        Loads all sheets of an Excel workbook into Pandas DataFrames and
        generates rich schema metadata for each sheet.

        Metadata per sheet includes:
            - columns         : list of column names
            - shape           : (rows, cols) tuple
            - dtypes          : {col_name: dtype_str}
            - numeric_stats   : {col_name: {min, max, mean}} for numeric columns
            - sample_values   : {col_name: [up to 3 non-null sample values]}

        Returns:
            sheets   (dict): {sheet_name: DataFrame}
            metadata (dict): {sheet_name: {columns, shape, dtypes, numeric_stats, sample_values}}
        """
        if not os.path.exists(file_path):
            return {}, {}

        try:
            excel_file = pd.ExcelFile(file_path, engine="calamine")
        except Exception:
            excel_file = pd.ExcelFile(file_path, engine="openpyxl", engine_kwargs={"data_only": True})
        sheets: dict[str, pd.DataFrame] = {}
        metadata: dict = {}

        for sheet in excel_file.sheet_names:
            df = excel_file.parse(sheet_name=sheet)
            sheets[sheet] = df

            # --- Basic schema ---
            dtypes = {str(col): str(dtype) for col, dtype in df.dtypes.items()}

            # --- Numeric statistics ---
            numeric_stats: dict = {}
            numeric_cols = df.select_dtypes(include="number").columns
            for col in numeric_cols:
                series = df[col].dropna()
                if not series.empty:
                    numeric_stats[str(col)] = {
                        "min":  round(float(series.min()), 4),
                        "max":  round(float(series.max()), 4),
                        "mean": round(float(series.mean()), 4),
                    }

            # --- Sample values (first 3 non-null values per column) ---
            sample_values: dict = {}
            for col in df.columns:
                non_null = df[col].dropna()
                samples = non_null.head(3).tolist()
                # Convert to safe serialisable types
                sample_values[str(col)] = [
                    str(v) if not isinstance(v, (int, float, bool)) else v
                    for v in samples
                ]

            metadata[sheet] = {
                "columns":       list(df.columns),
                "shape":         df.shape,
                "dtypes":        dtypes,
                "numeric_stats": numeric_stats,
                "sample_values": sample_values,
            }

        return sheets, metadata
