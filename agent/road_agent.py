import os
import re
import json
import datetime
from dataclasses import asdict

from llm.base_model import BaseLLM
from llm.llm_factory import LLMFactory
from llm.prompts import CODE_GENERATION_PROMPT, NARRATION_PROMPT, RETRY_PROMPT
from tools.code_executor import CodeExecutor
from data.schema_formatter import SchemaFormatter
from nlp.intent_parser import IntentParser
from config.settings import TEMP_FOLDER, LOGS_FOLDER, MAX_RETRIES, LLM_PROVIDER


class RoadAgent:

    def __init__(self, model: BaseLLM = None):
        self.llm           = model or LLMFactory.create()
        self.intent_parser = IntentParser(self.llm)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def answer(self, question: str, dataset_store: dict, metadata: dict) -> dict:
        """
        Statelessly processes a natural language question through the full pipeline:
            1. Intent Parsing    → RoadQuery
            2. Schema Formatting → schema string for LLM
            3. Code Generation   → Python pandas code
            4. Code Execution    → analytical result (with retry loop)
            5. Narration         → natural language answer

        Args:
            question      (str):  User's natural language question.
            dataset_store (dict): Hierarchical dict of DataFrames.
            metadata      (dict): Dataset schemas from DataFrameStore.get_metadata().

        Returns:
            dict with keys: question, road_query, generated_code, raw_result,
                            final_answer, timestamp
        """
        timestamp = datetime.datetime.now().isoformat()

        # --- Step 1: Parse intent → RoadQuery ---
        road_query      = self.intent_parser.parse(question)
        road_query_json = json.dumps(asdict(road_query), indent=2)

        # --- Step 2: Format schema ---
        schema_str = SchemaFormatter.format_schema(metadata)

        # --- Step 3 & 4: Code generation + execution loop ---
        system_prompt = CODE_GENERATION_PROMPT.format(
            schema=schema_str,
            road_query_json=road_query_json,
        )
        user_prompt = (
            f"Generate the pandas Python code to answer this question: {question}"
        )

        last_code   = ""
        last_result = None
        last_stdout = ""
        success     = False

        for attempt in range(MAX_RETRIES):
            try:
                llm_response = self.llm.generate(system_prompt, user_prompt)
                code         = self._extract_code(llm_response)
                last_code    = code

                self._save_generated_code(code)

                exec_result = CodeExecutor.execute_python(code, dataset_store, metadata)

                if exec_result["success"]:
                    last_result = exec_result["result"]
                    last_stdout = exec_result["stdout"]
                    success     = True
                    break
                else:
                    tb          = exec_result["traceback"] or exec_result["error"] or "Unknown error"
                    # On retry: rebuild prompt with error context + schema reminder
                    user_prompt = RETRY_PROMPT.format(
                        code=code,
                        traceback=tb,
                        schema=schema_str,
                    )
                    system_prompt = CODE_GENERATION_PROMPT.format(
                        schema=schema_str,
                        road_query_json=road_query_json,
                    )
            except Exception as e:
                user_prompt = (
                    f"Code generation raised an exception: {str(e)}. "
                    "Correct the code and try again."
                )

        # --- Step 5: Narration ---
        if success:
            narrator_sys  = NARRATION_PROMPT.format(
                road_query_json=road_query_json,
                result=str(last_result),
                stdout=last_stdout,
            )
            narrator_user = "Convert the execution output into a natural spoken-language response."
            try:
                final_answer = self.llm.generate(narrator_sys, narrator_user)
            except Exception as e:
                final_answer = (
                    f"The computed result is {last_result}. "
                    f"Voice narration failed: {str(e)}"
                )
        else:
            final_answer = (
                "I was unable to complete the analysis after multiple attempts. "
                "Please check that the question refers to columns that exist in the "
                "uploaded dataset, and try again."
            )

        result_dict = {
            "question":       question,
            "road_query":     road_query,
            "generated_code": last_code,
            "raw_result":     last_result,
            "final_answer":   final_answer,
            "timestamp":      timestamp,
        }

        # --- Step 6: Log interaction ---
        self._log_interaction(result_dict)

        return result_dict

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _extract_code(llm_response: str) -> str:
        """Extracts the Python code block from the LLM response."""
        # Try ```python ... ```
        match = re.search(r"```python\s*(.*?)\s*```", llm_response, re.DOTALL)
        if match:
            return match.group(1).strip()
        # Fallback: any generic ``` ... ```
        match = re.search(r"```\s*(.*?)\s*```", llm_response, re.DOTALL)
        if match:
            return match.group(1).strip()
        # Last resort: return as-is
        return llm_response.strip()

    @staticmethod
    def _save_generated_code(code: str):
        """Saves the generated code to temp/generated_code.py for audit."""
        os.makedirs(TEMP_FOLDER, exist_ok=True)
        path = os.path.join(TEMP_FOLDER, "generated_code.py")
        with open(path, "w", encoding="utf-8") as f:
            f.write("# Auto-generated analytics code\n")
            f.write(code)

    @staticmethod
    def _log_interaction(entry: dict):
        """
        Appends the interaction to a daily JSONL log file in logs/.
        road_query is serialised via dataclasses.asdict for JSON compatibility.
        """
        try:
            os.makedirs(LOGS_FOLDER, exist_ok=True)
            date_str  = datetime.datetime.now().strftime("%Y%m%d")
            log_path  = os.path.join(LOGS_FOLDER, f"conversation_{date_str}.jsonl")

            log_entry = {
                "timestamp":      entry["timestamp"],
                "provider":       LLM_PROVIDER,
                "question":       entry["question"],
                "road_query":     asdict(entry["road_query"]),
                "generated_code": entry["generated_code"],
                "raw_result":     str(entry["raw_result"]),
                "final_answer":   entry["final_answer"],
            }

            with open(log_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
        except Exception:
            pass  # Logging failures must never crash the main pipeline
