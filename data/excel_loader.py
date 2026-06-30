import os
import re
import pandas as pd


class ExcelLoader:

    @staticmethod
    def load_excel(file_path: str) -> tuple[dict[str, pd.DataFrame], dict]:
        """
        Loads all sheets of an Excel workbook into Pandas DataFrames and
        generates rich schema metadata for each sheet. Reconstructs headers
        by merging multi-row labels, carrying forward lane identifiers,
        and stripping trailing/leading whitespaces.
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
            try:
                df = ExcelLoader._parse_sheet_intelligently(excel_file, sheet)
            except Exception as e:
                print(f"ExcelLoader: Error parsing sheet '{sheet}' intelligently: {e}. Falling back to default.")
                df = excel_file.parse(sheet_name=sheet)
                df.columns = [re.sub(r"\s+", " ", str(c)).strip() for c in df.columns]

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

    @staticmethod
    def _parse_sheet_intelligently(excel_file, sheet_name) -> pd.DataFrame:
        """
        Parses a sheet, automatically detects multi-row headers,
        carries forward lane labels, merges titles, and cleans up whitespaces.
        """
        df_raw = excel_file.parse(sheet_name=sheet_name, header=None)

        if df_raw.empty:
            return df_raw

        # 1. Detect chainage columns to define where data starts
        chainage_cols = []
        for r_idx in range(min(5, df_raw.shape[0])):
            for c_idx in range(df_raw.shape[1]):
                val = str(df_raw.iloc[r_idx, c_idx]).lower()
                if "chainage" in val or "ch." in val or "ch " in val:
                    chainage_cols.append(c_idx)
        chainage_cols = list(set(chainage_cols))

        # Find the first row where any chainage column contains a valid number
        data_start_row = None
        for r_idx in range(df_raw.shape[0]):
            is_data = False
            for c_idx in chainage_cols:
                val = df_raw.iloc[r_idx, c_idx]
                try:
                    f_val = float(val)
                    if pd.notna(f_val) and f_val >= 0:
                        is_data = True
                        break
                except (ValueError, TypeError):
                    pass
            if is_data:
                data_start_row = r_idx
                break

        # Fallback to row 1 if no numerical chainage found
        if data_start_row is None:
            data_start_row = 1

        # The header rows are all rows from 0 to data_start_row - 1
        header_rows = df_raw.iloc[:data_start_row]

        new_cols = []
        carried_headers = []

        # Carry forward lane labels horizontally
        for r_idx in range(header_rows.shape[0]):
            row_vals = header_rows.iloc[r_idx].tolist()
            carried_row = []
            active_group = None
            for val in row_vals:
                s_val = str(val).strip() if pd.notna(val) else ""
                # Check for standard lane prefixes
                is_lane = any(s_val == x for x in ["L1", "L2", "L3", "L4", "R1", "R2", "R3", "R4"])
                if is_lane:
                    active_group = s_val
                elif s_val != "" and not any(s_val.startswith(x) for x in ["Limitation", "Remark", "Lane Roughness", "Rut Depth"]):
                    active_group = None
                carried_row.append(active_group if active_group else s_val)
            carried_headers.append(carried_row)

        # Merge headers down each column
        seen_cols = {}
        for c_idx in range(df_raw.shape[1]):
            col_parts = []
            for r_idx in range(len(carried_headers)):
                val = carried_headers[r_idx][c_idx]
                if val and str(val).lower() not in ["nan", "none", ""]:
                    col_parts.append(str(val))

            # Deduplicate consecutive matching tokens
            dedup_parts = []
            for part in col_parts:
                if not dedup_parts or dedup_parts[-1] != part:
                    dedup_parts.append(part)

            joined = " ".join(dedup_parts)
            # Normalize whitespace
            clean_name = re.sub(r"\s+", " ", joined).strip()
            
            # Ensure unique column names to prevent duplicate Series error
            if clean_name in seen_cols:
                seen_cols[clean_name] += 1
                clean_name = f"{clean_name}_{seen_cols[clean_name]}"
            else:
                seen_cols[clean_name] = 0
                
            new_cols.append(clean_name)

        # Clean the data slice and assign columns
        df_clean = df_raw.iloc[data_start_row:].copy()
        df_clean.columns = new_cols
        
        # Eliminate empty rows and columns that have Unnamed headings
        df_clean = df_clean.dropna(how="all")
        df_clean = df_clean.reset_index(drop=True)

        return df_clean

