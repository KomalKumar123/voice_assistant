import streamlit as st


class DataFrameStore:
    # Internal class variables to act as a fallback in non-Streamlit environments (like CLI tests)
    _cli_dfs = {}
    _cli_metadata = {}

    @classmethod
    def set_data(cls, dfs: dict, metadata: dict):
        try:
            st.session_state.dfs = dfs
            st.session_state.metadata = metadata
        except Exception:
            cls._cli_dfs = dfs
            cls._cli_metadata = metadata

    @classmethod
    def get_dfs(cls) -> dict:
        try:
            return st.session_state.get("dfs", cls._cli_dfs)
        except Exception:
            return cls._cli_dfs

    @classmethod
    def get_metadata(cls) -> dict:
        try:
            return st.session_state.get("metadata", cls._cli_metadata)
        except Exception:
            return cls._cli_metadata

    @classmethod
    def get_sheet_names(cls) -> list[str]:
        try:
            return list(st.session_state.get("dfs", cls._cli_dfs).keys())
        except Exception:
            return list(cls._cli_dfs.keys())
