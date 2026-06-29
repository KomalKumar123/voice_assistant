import re
import json
from models.road_query import RoadQuery
from llm.base_model import BaseLLM
from llm.prompts import INTENT_PARSER_SYSTEM_PROMPT
from data.road_concepts import ROAD_CONCEPTS
from metadata.road_registry import RoadRegistry


class IntentParser:

    def __init__(self, model: BaseLLM):
        self.model = model

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def parse(self, question: str) -> RoadQuery:
        """
        Parses a natural language question into a structured RoadQuery.

        Strips Qwen3 <think>…</think> blocks before JSON parsing.
        Returns a safe default RoadQuery on any parsing failure.
        """
        registry = RoadRegistry.get_registry()

        available_roads  = []
        available_months = []
        for dataset_id, info in registry.items():
            available_roads.append(f"{info['name']} (ID: {dataset_id})")
            available_months.extend(info.get("available_sheets", []))

        available_months = list(set(available_months))

        system_prompt = INTENT_PARSER_SYSTEM_PROMPT.format(
            available_roads=json.dumps(available_roads),
            available_months=json.dumps(available_months),
            road_concepts=json.dumps(ROAD_CONCEPTS, indent=2),
        )

        user_prompt = f"Parse this question into the RoadQuery JSON schema: {question}"

        try:
            raw_response = self.model.generate(
                system_prompt,
                user_prompt,
                response_format="json",
                max_tokens=256,   # compact JSON output — never needs more than 256 tokens
            )
            cleaned      = self._strip_think_tags(raw_response)
            data         = self._parse_json(cleaned)
            return self._build_road_query(data)
        except Exception as e:
            # Graceful degradation — return a safe default rather than crashing
            return RoadQuery(intent="general", analysis_type="aggregation")

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _strip_think_tags(text: str) -> str:
        """
        Removes Qwen3-style <think>…</think> reasoning blocks and markdown
        code fences from the raw model output, leaving only the JSON payload.
        """
        # Remove <think>…</think> (including multiline)
        text = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL)
        # Remove markdown json fences if present
        text = re.sub(r"```json\s*", "", text)
        text = re.sub(r"```\s*", "", text)
        return text.strip()

    @staticmethod
    def _parse_json(text: str) -> dict:
        """Attempts JSON parsing; raises on failure."""
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            # Last-ditch: find the first {...} block in the text
            match = re.search(r"\{.*\}", text, re.DOTALL)
            if match:
                return json.loads(match.group())
            raise

    @staticmethod
    def _build_road_query(data: dict) -> RoadQuery:
        return RoadQuery(
            intent=data.get("intent", "general"),
            analysis_type=data.get("analysis_type", "aggregation"),
            primary_metric=data.get("primary_metric"),
            secondary_metrics=data.get("secondary_metrics", []),
            operation=data.get("operation"),
            top_k=data.get("top_k", 1),
            grouping=data.get("grouping"),
            filters=data.get("filters", []),
            comparison_targets=data.get("comparison_targets", []),
            road_identifiers=data.get("road_identifiers", []),
            time_periods=data.get("time_periods", []),
            chainage_range=data.get("chainage_range"),
        )
