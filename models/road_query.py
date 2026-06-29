from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class RoadQuery:
    intent: str
    analysis_type: str  # e.g., "ranking", "comparison", "trend", "anomaly", "aggregation"
    primary_metric: Optional[str] = None
    secondary_metrics: List[str] = field(default_factory=list)
    operation: Optional[str] = None
    top_k: int = 1
    grouping: Optional[str] = None
    filters: List[dict] = field(default_factory=list)
    comparison_targets: List[str] = field(default_factory=list)
    road_identifiers: List[str] = field(default_factory=list)
    time_periods: List[str] = field(default_factory=list)
    chainage_range: Optional[str] = None
