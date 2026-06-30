class SchemaFormatter:

    @staticmethod
    def format_schema(metadata: dict) -> str:
        """
        Formats the hierarchical metadata dictionary into a concise, LLM-readable
        schema string that includes column names, dtypes, numeric stats, and samples.

        Input structure:
        {
            "dataset_id": {
                "name": "Road_A",
                "metadata": {
                    "Sheet_Name": {
                        "columns":       [...],
                        "shape":         (rows, cols),
                        "dtypes":        {col: dtype},
                        "numeric_stats": {col: {min, max, mean}},
                        "sample_values": {col: [v1, v2, v3]}
                    }
                }
            }
        }
        """
        if not metadata:
            return "No metadata available."

        output = []

        for dataset_id, info in metadata.items():
            dataset_name = info["name"]
            output.append(f"=== Dataset: {dataset_name} (ID: {dataset_id}) ===")

            for sheet_name, sheet_info in info.get("metadata", {}).items():
                rows, cols = sheet_info["shape"]
                output.append(f"\n  Sheet: '{sheet_name}'  ({rows} rows × {cols} columns)")
                output.append("  Columns:")

                dtypes        = sheet_info.get("dtypes", {})
                numeric_stats = sheet_info.get("numeric_stats", {})
                sample_values = sheet_info.get("sample_values", {})

                for col in sheet_info.get("columns", []):
                    col_str  = str(col)
                    dtype    = dtypes.get(col_str, "unknown")
                    samples  = sample_values.get(col_str, [])
                    stats    = numeric_stats.get(col_str)

                    line = f"    - '{col_str}' [{dtype}]"

                    # Append numeric stats if available
                    if stats:
                        line += (
                            f"  min={stats['min']}, max={stats['max']}, "
                            f"mean={stats['mean']}"
                        )

                    # Append sample values
                    if samples:
                        sample_str = ", ".join(str(s) for s in samples[:3])
                        line += f"  samples=[{sample_str}]"

                    output.append(line)

            output.append("")  # blank line between datasets

        return "\n".join(output).strip()

    @staticmethod
    def format_flat_schema(flat_df) -> str:
        """
        Formats a schema description of the flat DataFrame for LLM consumption,
        detailing the columns, data types, numeric summaries, and sample values.
        """
        import pandas as pd
        if flat_df.empty:
            return "No active data."

        output = []
        rows, cols = flat_df.shape
        output.append(f"=== Unified DataFrame `flat_df` ({rows} rows × {cols} columns) ===")
        output.append("Columns:")

        for col in flat_df.columns:
            col_str = str(col)
            dtype = str(flat_df[col].dtype)
            
            # Extract samples (first 3 non-null)
            non_null = flat_df[col].dropna()
            samples = non_null.head(3).tolist()
            sample_vals = [
                str(v) if not isinstance(v, (int, float, bool)) else v
                for v in samples
            ]
            
            line = f"  - '{col_str}' [{dtype}]"
            
            # Extract numeric stats if relevant
            if pd.api.types.is_numeric_dtype(flat_df[col]):
                if not non_null.empty:
                    try:
                        min_v = round(float(non_null.min()), 4)
                        max_v = round(float(non_null.max()), 4)
                        mean_v = round(float(non_null.mean()), 4)
                        line += f"  min={min_v}, max={max_v}, mean={mean_v}"
                    except Exception:
                        pass
                        
            if sample_vals:
                sample_str = ", ".join(str(s) for s in sample_vals)
                line += f"  samples=[{sample_str}]"
                
            output.append(line)

        return "\n".join(output)

