import streamlit as st
from data.file_manager import FileManager
from data.excel_loader import ExcelLoader
from data.dataframe_store import DataFrameStore


def upload_file_ui():
    """
    Renders the file upload UI. Disappears once file is successfully uploaded and loaded.
    """
    # If file is already uploaded, hide the upload component
    if st.session_state.get("file_uploaded", False):
        return

    st.subheader("Upload Highway Data Sheet")
    
    uploaded_file = st.file_uploader(
        "Upload Excel File (.xlsx)",
        type=["xlsx"],
        key="excel_uploader"
    )

    if uploaded_file is not None:
        with st.spinner("Processing Excel file and loading sheets..."):
            try:
                # Save file locally as uploaded_files/current.xlsx
                file_path = FileManager.save_uploaded_file(uploaded_file)

                # Load workbook sheets and generate metadata
                dfs, metadata = ExcelLoader.load_excel(file_path)

                # Store in central store (and session state)
                st.session_state.file_path = file_path
                DataFrameStore.set_data(dfs, metadata)
                
                st.session_state.file_uploaded = True
                st.success("Workbook sheets loaded successfully!")
                
                # Rerun Streamlit to update the layout and hide this component
                st.rerun()
            except Exception as e:
                st.error(f"Error loading Excel: {str(e)}")