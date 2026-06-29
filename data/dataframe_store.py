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
