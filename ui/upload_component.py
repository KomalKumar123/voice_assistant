import streamlit as st
from data.file_manager import FileManager
from data.excel_loader import ExcelLoader
from data.dataframe_store import DataFrameStore
from metadata.road_registry import RoadRegistry


def upload_file_ui():
    """
    Renders the multi-file dataset uploader in the sidebar.
    Supports uploading multiple Excel workbooks simultaneously.
    Each file is stored with a unique ID so datasets never overwrite each other.
    """
    uploaded_files = st.file_uploader(
        "Upload Excel Workbook(s)",
        type=["xlsx"],
        accept_multiple_files=True,
        key="excel_uploader",
        help="Upload one or more road survey Excel workbooks (.xlsx)",
        label_visibility="collapsed",
    )

    if uploaded_files:
        existing_registry = RoadRegistry.get_registry()
        new_file_loaded = False

        for uploaded_file in uploaded_files:
            # Derive a unique dataset_id from the registry size
            dataset_id = f"dataset_{len(DataFrameStore.get_dataset_store()) + 1}"

            # Skip if this filename is already registered (prevents re-processing on rerender)
            already_loaded = any(
                info.get("source_filename") == uploaded_file.name
                for info in existing_registry.values()
            )
            if already_loaded:
                continue

            name = uploaded_file.name.replace(".xlsx", "").replace("_", " ")

            with st.spinner(f"Loading '{name}'…"):
                try:
                    file_path = FileManager.save_uploaded_file(uploaded_file, dataset_id)
                    sheets, metadata = ExcelLoader.load_excel(file_path)
                    DataFrameStore.add_dataset(dataset_id, name, sheets, metadata)

                    available_sheets = list(sheets.keys())
                    RoadRegistry.register_dataset(
                        dataset_id,
                        name,
                        file_path,
                        available_sheets,
                        source_filename=uploaded_file.name,
                    )

                    st.session_state.file_uploaded = True
                    new_file_loaded = True
                    st.success(f"✅ '{name}' loaded — {len(available_sheets)} sheet(s)")

                except Exception as e:
                    st.error(f"❌ Failed to load '{uploaded_file.name}': {str(e)}")

        # Trigger a rerun to refresh the sidebar registry display only if a new file was loaded
        if new_file_loaded:
            st.rerun()


def render_sidebar_registry(registry: dict):
    """
    Renders styled dataset cards in the sidebar for each loaded dataset.

    Args:
        registry (dict): RoadRegistry.get_registry() output.
    """
    for dataset_id, info in registry.items():
        name   = info["name"]
        sheets = info.get("available_sheets", [])

        sheet_tags = "".join(
            f'<span class="ds-sheet">{s}</span>' for s in sheets
        )

        st.markdown(
            f"""
            <div class="dataset-card">
                <div class="ds-name">🛣️ {name}</div>
                <div class="ds-id">{dataset_id}</div>
                <div style="margin-top:0.4rem;">{sheet_tags}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )