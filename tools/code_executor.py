import sys
import io
import ast
import traceback


# Identifiers that generated code must never use
_BLOCKED_NAMES = frozenset({
    "open", "exec", "eval", "compile", "__import__",
    "subprocess", "os", "sys", "shutil", "socket",
    "importlib", "builtins",
})


class CodeExecutor:

    @staticmethod
    def execute_python(code: str, dataset_store: dict, metadata: dict = None) -> dict:
        """
        Safely executes LLM-generated Python analytics code.

        The execution context provides:
            - dataset_store  : hierarchical dict of {dataset_id: {name, sheets}}
            - pd             : pandas
            - np             : numpy
            - datetime       : datetime module
            - json           : json module
            - metadata       : dataset schema metadata

        The generated code MUST assign its final answer to a variable named `result`.

        Returns:
            dict: {
                "success":   bool,
                "result":    Any,
                "stdout":    str,
                "error":     str | None,
                "traceback": str | None
            }
        """
        # --- Security pre-check via AST ---
        security_error = CodeExecutor._check_security(code)
        if security_error:
            return {
                "success":   False,
                "result":    None,
                "stdout":    "",
                "error":     security_error,
                "traceback": security_error,
            }

        # --- Execution environment ---
        import pandas as pd    # noqa: PLC0415
        import numpy as np     # noqa: PLC0415
        import datetime as dt  # noqa: PLC0415
        import json as _json   # noqa: PLC0415

        exec_globals = {
            "pd":           pd,
            "np":           np,
            "datetime":     dt,
            "json":         _json,
            "dataset_store": dataset_store,
            "metadata":     metadata or {},
        }
        exec_locals = {"result": None}

        # --- Capture stdout ---
        stdout_capture = io.StringIO()
        old_stdout     = sys.stdout
        sys.stdout     = stdout_capture

        success = True
        error   = None
        tb      = None

        try:
            exec(code, exec_globals, exec_locals)  # noqa: S102
        except Exception as e:
            success = False
            error   = str(e)
            tb      = traceback.format_exc()
        finally:
            sys.stdout = old_stdout

        return {
            "success":   success,
            "result":    exec_locals.get("result"),
            "stdout":    stdout_capture.getvalue(),
            "error":     error,
            "traceback": tb,
        }

    @staticmethod
    def _check_security(code: str) -> str | None:
        """
        Parses the code with AST and blocks dangerous identifier usage.
        Returns an error string if blocked; None if safe.
        """
        try:
            tree = ast.parse(code)
        except SyntaxError as e:
            return f"Syntax error in generated code: {e}"

        for node in ast.walk(tree):
            # Block dangerous function calls and attribute access
            if isinstance(node, ast.Name) and node.id in _BLOCKED_NAMES:
                return (
                    f"Security violation: use of '{node.id}' is not permitted "
                    "in generated analytics code."
                )
            if isinstance(node, ast.Attribute) and node.attr in _BLOCKED_NAMES:
                return (
                    f"Security violation: attribute '{node.attr}' is not permitted."
                )
            # Block bare import statements
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                return (
                    "Security violation: import statements are not allowed "
                    "in generated analytics code."
                )

        return None
