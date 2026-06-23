import os
import re
from llm.prompts import CODE_GENERATION_PROMPT, NARRATION_PROMPT, RETRY_PROMPT
from tools.code_executor import CodeExecutor
from data.schema_formatter import SchemaFormatter
from config.settings import TEMP_FOLDER


class RoadAgent:

    def __init__(self):
        # Instantiate LLM abstraction (GeminiLLM under the hood)
        from llm.gemini_model import GeminiLLM
        self.llm = GeminiLLM()

    def _extract_code(self, llm_response: str) -> str:
        """
        Parses code blocks out of the LLM response.
        """
        # Search for ```python ... ```
        match = re.search(r"```python\s*(.*?)\s*```", llm_response, re.DOTALL)
        if match:
            return match.group(1).strip()
        # Fallback to any generic code block ``` ... ```
        match = re.search(r"```\s*(.*?)\s*```", llm_response, re.DOTALL)
        if match:
            return match.group(1).strip()
        # Fallback if no block was formatted but code was outputted
        return llm_response.strip()

    def _save_generated_code(self, code: str):
        """
        Saves the generated python code to temp/generated_code.py for audit.
        """
        os.makedirs(TEMP_FOLDER, exist_ok=True)
        code_file_path = os.path.join(TEMP_FOLDER, "generated_code.py")
        with open(code_file_path, "w", encoding="utf-8") as f:
            f.write("# Generated code for execution\n")
            f.write(code)

    def answer(self, question: str, dfs: dict, metadata: dict) -> dict:
        """
        Statelessly processes a natural language question.
        
        Args:
            question (str): User's natural language query.
            dfs (dict): Dictionary of loaded DataFrames.
            metadata (dict): Metadata schemas.
            
        Returns:
            dict: {
                "question": str,
                "generated_code": str,
                "raw_result": Any,
                "final_answer": str
            }
        """
        # 1. Format metadata schema
        schema_str = SchemaFormatter.format_schema(metadata)
        
        # 2. Setup prompts
        system_prompt = CODE_GENERATION_PROMPT.format(schema=schema_str, question=question)
        user_prompt = f"Write the Python pandas code to answer: {question}"
        
        last_code = ""
        last_result = None
        last_stdout = ""
        success = False
        attempts = 3
        
        # 3. Code generation & execution loop with retries
        for i in range(attempts):
            try:
                # Call LLM statelessly
                llm_response = self.llm.generate(system_prompt, user_prompt)
                code = self._extract_code(llm_response)
                last_code = code
                
                # Save code to temp file
                self._save_generated_code(code)
                
                # Execute code
                exec_result = CodeExecutor.execute_python(code, dfs)
                
                if exec_result["success"]:
                    last_result = exec_result["result"]
                    last_stdout = exec_result["stdout"]
                    success = True
                    break
                else:
                    # Capture traceback and error
                    tb = exec_result["traceback"] or exec_result["error"] or "Unknown error"
                    # Repurpose user prompt to instruct correction
                    user_prompt = RETRY_PROMPT.format(code=code, traceback=tb)
            except Exception as e:
                user_prompt = f"Code generation or setup failed with exception: {str(e)}. Try again."

        # 4. Narration step
        if success:
            narrator_sys = NARRATION_PROMPT.format(
                question=question,
                result=str(last_result),
                stdout=last_stdout
            )
            narrator_user = "Convert the execution output into a natural conversational speech response."
            
            try:
                final_answer = self.llm.generate(narrator_sys, narrator_user)
            except Exception as e:
                final_answer = f"I computed the result as {last_result}, but failed to voice-narrate it: {str(e)}"
        else:
            final_answer = "I apologize, but I encountered errors executing the analysis code on the dataset."
            if user_prompt:
                # Include some debugging context if retry failed
                final_answer += f" Last error detail: {user_prompt[:200]}"
                
        return {
            "question": question,
            "generated_code": last_code,
            "raw_result": last_result,
            "final_answer": final_answer
        }
