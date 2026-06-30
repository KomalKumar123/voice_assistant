import re
import json
from models.road_query import RoadQuery
from llm.base_model import BaseLLM
from llm.prompts import INTENT_PARSER_SYSTEM_PROMPT
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
        Strips reasoning blocks, cleans JSON formatting, and falls back to a safe default on error.
        """
        registry = RoadRegistry.get_registry()

        available_roads  = []
        available_months = []
        for dataset_id, info in registry.items():
            available_roads.append(info['name'])
            available_months.extend(info.get("available_sheets", []))

        # Deduplicate periods
        available_months = list(set(available_months))
        # Remove empty strings
        available_roads = [r for r in available_roads if r]
        available_months = [m for m in available_months if m]

        system_prompt = INTENT_PARSER_SYSTEM_PROMPT.format(
            available_roads=json.dumps(available_roads),
            available_months=json.dumps(available_months),
        )

        user_prompt = f"Extract parameters from this question: {question}"

        try:
            raw_response = self.model.generate(
                system_prompt,
                user_prompt,
                response_format="json",
                max_tokens=256,
            )
            cleaned      = self._strip_think_tags(raw_response)
            data         = self._parse_json(cleaned)
            return self._build_road_query(data)
        except Exception as e:
            print(f"IntentParser: Failed parsing user question '{question}' due to: {e}. Returning fallback.")
            return RoadQuery(metric="any", operation="list", lane="any", road_name="any", survey_period="any")

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _strip_think_tags(text: str) -> str:
        """
        Removes <think>...</think> blocks and code blocks to leave only the raw JSON.
        """
        text = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL)
        text = re.sub(r"```json\s*", "", text)
        text = re.sub(r"```\s*", "", text)
        return text.strip()

    @staticmethod
    def _parse_json(text: str) -> dict:
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            match = re.search(r"\{.*\}", text, re.DOTALL)
            if match:
                return json.loads(match.group())
            raise

    @staticmethod
    def _build_road_query(data: dict) -> RoadQuery:
        # Convert chainage_start and chainage_end to float safely
        ch_start = data.get("chainage_start")
        ch_end = data.get("chainage_end")
        
        try:
            ch_start = float(ch_start) if ch_start is not None else None
        except (ValueError, TypeError):
            ch_start = None
            
        try:
            ch_end = float(ch_end) if ch_end is not None else None
        except (ValueError, TypeError):
            ch_end = None

        return RoadQuery(
            metric=data.get("metric", "any"),
            operation=data.get("operation", "list"),
            lane=data.get("lane", "any"),
            road_name=data.get("road_name", "any"),
            survey_period=data.get("survey_period", "any"),
            chainage_start=ch_start,
            chainage_end=ch_end,
            top_k=data.get("top_k", 1),
        )

