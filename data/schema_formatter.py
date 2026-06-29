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
