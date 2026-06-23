class SchemaFormatter:

    @staticmethod
    def format_schema(metadata: dict) -> str:
        """
        Formats the metadata dictionary into a clean text schema representation
        for the LLM.
        """
        if not metadata:
            return "No metadata available."
            
        output = []
        for sheet, info in metadata.items():
            output.append(f"Sheet: {sheet}")
            output.append("Columns:")
            for col, dtype in info.get("dtypes", {}).items():
                output.append(f"  {col} : {dtype}")
            output.append("")  # Empty line between sheets
            
        return "\n".join(output).strip()
