import streamlit as st


class RoadRegistry:
    # CLI fallback registry for non-Streamlit environments
    _cli_registry: dict = {}

    @classmethod
    def register_dataset(
        cls,
        dataset_id: str,
        name: str,
        file_path: str,
        available_sheets: list[str],
        source_filename: str = "",
    ):
        """
        Registers dataset metadata dynamically in memory.

        Args:
            dataset_id       (str):  Unique identifier, e.g. 'dataset_1'.
            name             (str):  Human-readable road/dataset name.
            file_path        (str):  Path to the saved Excel file on disk.
            available_sheets (list): Sheet names (survey months) in the workbook.
            source_filename  (str):  Original uploaded filename — used to detect
                                     duplicate uploads across Streamlit rerenders.
        """
        entry = {
            "name":             name,
            "file_path":        file_path,
            "available_sheets": available_sheets,
            "source_filename":  source_filename,
        }
        try:
            if "road_registry" not in st.session_state:
                st.session_state.road_registry = {}
            st.session_state.road_registry[dataset_id] = entry
        except Exception:
            cls._cli_registry[dataset_id] = entry

    @classmethod
    def get_registry(cls) -> dict:
        """Returns the full registry dict."""
        try:
            return st.session_state.get("road_registry", cls._cli_registry)
        except Exception:
            return cls._cli_registry

    @classmethod
    def get_dataset_info(cls, dataset_id: str) -> dict:
        """Returns the registry entry for a specific dataset ID."""
        return cls.get_registry().get(dataset_id, {})
