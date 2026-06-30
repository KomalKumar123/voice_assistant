from dataclasses import dataclass
from typing import Optional


@dataclass
class RoadQuery:
    metric: str           # "roughness" | "rut_depth" | "cracking" | "potholes" | "any"
    operation: str        # "max" | "min" | "mean" | "sum" | "count" | "list"
    lane: str             # "L1" | "L2" | "R3" etc., or "any"
    road_name: str        # e.g. "Highway Alpha", or "any"
    survey_period: str    # e.g. "Mar-25", or "any"
    chainage_start: Optional[float] = None
    chainage_end: Optional[float] = None
    top_k: int = 1

