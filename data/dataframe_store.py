import streamlit as st
import pandas as pd


class DataFrameStore:
    # CLI fallback database store
    _cli_dataset_store = {}

    @classmethod
    def add_dataset(cls, dataset_id: str, name: str, sheets: dict[str, pd.DataFrame], metadata: dict):
        """
        Stores loaded sheets and metadata for a given dataset ID.
        """
        try:
            if "dataset_store" not in st.session_state:
                st.session_state.dataset_store = {}
            st.session_state.dataset_store[dataset_id] = {
                "name": name,
                "sheets": sheets,
                "metadata": metadata
            }
        except Exception:
            cls._cli_dataset_store[dataset_id] = {
                "name": name,
                "sheets": sheets,
                "metadata": metadata
            }

    @classmethod
    def get_dataset_store(cls) -> dict:
        """
        Retrieves the complete hierarchical dataset store:
        {
            "dataset_1": {
                "name": "Road_A",
                "sheets": {"Jul-24": DataFrame, "Mar-25": DataFrame},
                "metadata": {"Jul-24": {...}, "Mar-25": {...}}
            }
        }
        """
        try:
            return st.session_state.get("dataset_store", cls._cli_dataset_store)
        except Exception:
            return cls._cli_dataset_store

    @classmethod
    def get_dataset_names(cls) -> list[str]:
        """
        Returns a list of all registered dataset names.
        """
        return [info["name"] for info in cls.get_dataset_store().values()]

    @classmethod
    def get_metadata(cls) -> dict:
        """
        Returns a dictionary of schemas structured by dataset.
        """
        metadata = {}
        for dataset_id, info in cls.get_dataset_store().items():
            metadata[dataset_id] = {
                "name": info["name"],
                "metadata": info["metadata"]
            }
        return metadata

    @classmethod
    def generate_flat_df(cls) -> pd.DataFrame:
        """
        Compiles a single, normalized, tidy (melted) DataFrame by parsing all
        loaded datasets in dataset_store.
        Standardizes columns to:
          - dataset_name
          - sheet_name
          - survey_period
          - road_name
          - start_chainage
          - end_chainage
          - metric ('roughness' | 'rut_depth' | 'cracking' | 'potholes')
          - lane
          - value (float)
          - source_column
        """
        import re
        store = cls.get_dataset_store()
        if not store:
            return pd.DataFrame()

        melted_rows = []

        for dataset_id, info in store.items():
            dataset_name = info["name"]
            for sheet_name, df in info.get("sheets", {}).items():
                if "Summary" in sheet_name or "defect" in sheet_name.lower():
                    continue

                # 1. Locate chainage column indices
                start_ch_idx = None
                end_ch_idx = None

                for idx, col in enumerate(df.columns):
                    c_low = str(col).lower()
                    if "start chainage" in c_low:
                        start_ch_idx = idx
                    elif "end chainage" in c_low:
                        end_ch_idx = idx

                if start_ch_idx is None:
                    for idx, col in enumerate(df.columns):
                        c_low = str(col).lower()
                        if "chainage" in c_low:
                            start_ch_idx = idx
                            break

                if start_ch_idx is None:
                    continue  # skip sheets without chainage variables

                # 2. Extract survey period
                survey_period = "unknown"
                match = re.search(r"(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[-_\s]*\d{2,4}", sheet_name, re.IGNORECASE)
                if match:
                    survey_period = match.group(0)
                elif "Jul-24" in sheet_name or "Jul 24" in sheet_name:
                    survey_period = "Jul-24"
                elif "Mar-25" in sheet_name or "Mar 25" in sheet_name:
                    survey_period = "Mar-25"

                is_pothole_sheet = "pothole" in sheet_name.lower() or "depression" in sheet_name.lower()

                if is_pothole_sheet:
                    # Potholes sheet mapping
                    lane_idx = None
                    area_idx = None
                    for idx, col in enumerate(df.columns):
                        c_low = str(col).lower()
                        if "lane" in c_low:
                            lane_idx = idx
                        elif "area" in c_low:
                            area_idx = idx

                    if lane_idx is not None and area_idx is not None:
                        s_ch = pd.to_numeric(df.iloc[:, start_ch_idx], errors="coerce")
                        area_val = pd.to_numeric(df.iloc[:, area_idx], errors="coerce")
                        
                        temp_df = pd.DataFrame({
                            "s_ch": s_ch,
                            "val": area_val,
                            "lane": df.iloc[:, lane_idx]
                        }).dropna(subset=["s_ch", "val"])

                        for idx, row in temp_df.iterrows():
                            melted_rows.append({
                                "dataset_name": dataset_name,
                                "sheet_name": sheet_name,
                                "survey_period": survey_period,
                                "road_name": dataset_name,
                                "start_chainage": float(row["s_ch"]),
                                "end_chainage": float(row["s_ch"]) + 100.0,
                                "metric": "potholes",
                                "lane": str(row["lane"]).strip(),
                                "value": float(row["val"]),
                                "source_column": str(df.columns[area_idx])
                            })
                else:
                    # Standard lane-based sheet (roughness, rutting, cracking, ravelling)
                    for col_idx, col in enumerate(df.columns):
                        col_str = str(col)
                        c_low = col_str.lower()
                        lane_match = re.search(r"\b(L1|L2|L3|L4|R1|R2|R3|R4)\b", col_str)
                        if not lane_match:
                            continue

                        lane = lane_match.group(1)

                        metric = None
                        if "roughness" in c_low or "bi" in c_low or "iri" in c_low:
                            metric = "roughness"
                        elif "rut" in c_low:
                            metric = "rut_depth"
                        elif "crack" in c_low or "cracking" in c_low or "ravelling" in c_low:
                            metric = "cracking"

                        if metric:
                            s_ch = pd.to_numeric(df.iloc[:, start_ch_idx], errors="coerce")
                            e_ch = pd.to_numeric(df.iloc[:, end_ch_idx], errors="coerce") if end_ch_idx is not None else s_ch + 100.0
                            vals = pd.to_numeric(df.iloc[:, col_idx], errors="coerce")

                            temp_df = pd.DataFrame({
                                "s_ch": s_ch,
                                "e_ch": e_ch,
                                "val": vals
                            }).dropna()

                            for idx, row in temp_df.iterrows():
                                melted_rows.append({
                                    "dataset_name": dataset_name,
                                    "sheet_name": sheet_name,
                                    "survey_period": survey_period,
                                    "road_name": dataset_name,
                                    "start_chainage": float(row["s_ch"]),
                                    "end_chainage": float(row["e_ch"]),
                                    "metric": metric,
                                    "lane": lane,
                                    "value": float(row["val"]),
                                    "source_column": col_str
                                })

        if not melted_rows:
            return pd.DataFrame()

        return pd.DataFrame(melted_rows)

    @classmethod
    def get_metadata_registry(cls) -> dict:
        """
        Dynamically extracts and returns a mapping of metric columns,
        lane assignments, and chainage variables across all loaded sheets.
        """
        registry = {
            "roughness_columns": [],
            "rut_columns": [],
            "crack_columns": [],
            "pothole_columns": []
        }
        
        store = cls.get_dataset_store()
        for dataset_id, info in store.items():
            for sheet_name, df in info.get("sheets", {}).items():
                for col in df.columns:
                    col_str = str(col)
                    c_low = col_str.lower()
                    if "roughness" in c_low or "bi" in c_low or "iri" in c_low:
                        registry["roughness_columns"].append(col_str)
                    elif "rut" in c_low:
                        registry["rut_columns"].append(col_str)
                    elif "crack" in c_low or "cracking" in c_low or "ravelling" in c_low:
                        registry["crack_columns"].append(col_str)
                    elif "potholes" in c_low or "pothole" in c_low:
                        registry["pothole_columns"].append(col_str)
                        
        # Deduplicate values
        for key in registry:
            registry[key] = list(set(registry[key]))
            
        return registry


