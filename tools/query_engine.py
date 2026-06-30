import pandas as pd
import numpy as np
import re
from models.road_query import RoadQuery


class DeterministicQueryEngine:

    @staticmethod
    def execute(road_query: RoadQuery, flat_df: pd.DataFrame) -> dict:
        """
        Executes analytical queries deterministically on the flat tidy DataFrame
        using parameters extracted by the IntentParser.
        """
        if flat_df.empty:
            return {"success": False, "error": "No dataset is currently loaded in memory."}

        df = flat_df.copy()

        # 1. Filter by Road Name (case-insensitive fuzzy match)
        if road_query.road_name and road_query.road_name.lower() != "any":
            road_target = road_query.road_name.lower().strip()
            df = df[df["road_name"].str.lower().str.strip().str.contains(road_target, regex=False)]

        # 2. Filter by Survey Period
        if road_query.survey_period and road_query.survey_period.lower() != "any":
            period_target = road_query.survey_period.lower().strip()
            df = df[df["survey_period"].str.lower().str.strip() == period_target]

        # 3. Filter by Metric
        if road_query.metric and road_query.metric.lower() != "any":
            metric_target = road_query.metric.lower().strip()
            # Handle ravelling synonym mapping to cracking
            if metric_target == "ravelling":
                metric_target = "cracking"
            df = df[df["metric"] == metric_target]

        # 4. Filter by Lane
        if road_query.lane and road_query.lane.lower() != "any":
            lane_target = road_query.lane.upper().strip()
            df = df[df["lane"].str.upper().str.strip() == lane_target]

        # 5. Filter by Chainage Range
        if road_query.chainage_start is not None:
            df = df[df["start_chainage"] >= road_query.chainage_start]
        if road_query.chainage_end is not None:
            df = df[df["end_chainage"] <= road_query.chainage_end]

        if df.empty:
            return {
                "success": False,
                "error": "No records found matching the specified filters (metric, road, lane, or period)."
            }

        # 6. Apply Aggregations & Operations
        op = str(road_query.operation).lower().strip()
        
        is_max = op in ["max", "maximum", "highest", "worst", "biggest"]
        is_min = op in ["min", "minimum", "lowest", "best", "smallest"]

        # Sort values: standard descending for maximums, ascending for minimums
        if is_max or is_min:
            df_sorted = df.sort_values(by="value", ascending=is_min)
            top_k = road_query.top_k or 1
            
            if top_k > 1 or op == "list":
                results = df_sorted.head(top_k).to_dict(orient="records")
                return {
                    "success": True,
                    "result": results,
                    "summary": f"List of top {len(results)} records"
                }
            else:
                extreme_record = df_sorted.iloc[0].to_dict()
                return {
                    "success": True,
                    "result": extreme_record,
                    "summary": "Extracted extreme value record"
                }

        if op in ["mean", "average", "avg"]:
            mean_val = df["value"].mean()
            return {
                "success": True,
                "result": float(mean_val) if pd.notna(mean_val) else None,
                "summary": "Mean average value"
            }

        if op in ["sum", "total"]:
            sum_val = df["value"].sum()
            return {
                "success": True,
                "result": float(sum_val) if pd.notna(sum_val) else None,
                "summary": "Sum total value"
            }

        if op in ["count", "number"]:
            count_val = df["value"].count()
            return {
                "success": True,
                "result": int(count_val),
                "summary": "Record count"
            }

        # Default listing: return top 5 records
        return {
            "success": True,
            "result": df.head(5).to_dict(orient="records"),
            "summary": "Listing records snippet"
        }
