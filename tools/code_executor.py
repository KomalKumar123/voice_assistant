import sys
import io
import traceback


class CodeExecutor:

    @staticmethod
    def execute_python(code: str, dfs: dict) -> dict:
        """
        Executes Python code.
        The code has access to 'dfs' (dictionary of sheets/DataFrames),
        'pd' (pandas), and 'np' (numpy).
        The final calculation must be assigned to 'result' (e.g. result = ...).
        
        Returns:
            dict: {
                "success": bool,
                "result": Any,
                "stdout": str,
                "error": str or None,
                "traceback": str or None
            }
        """
        stdout_capture = io.StringIO()
        # Save old stdout and redirect
        old_stdout = sys.stdout
        sys.stdout = stdout_capture

        exec_globals = {
            "pd": __import__("pandas"),
            "np": __import__("numpy"),
            "dfs": dfs,
        }
        exec_locals = {"result": None}

        success = True
        error = None
        tb = None

        try:
            exec(code, exec_globals, exec_locals)
        except Exception as e:
            success = False
            error = str(e)
            tb = traceback.format_exc()
        finally:
            # Restore stdout
            sys.stdout = old_stdout

        return {
            "success": success,
            "result": exec_locals.get("result"),
            "stdout": stdout_capture.getvalue(),
            "error": error,
            "traceback": tb
        }
