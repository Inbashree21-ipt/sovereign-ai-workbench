import subprocess
import sys
import tempfile
import os


def run_python_code(code: str) -> str:

    temp_file = None

    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".py",
            delete=False,
            encoding="utf-8"
        ) as file:

            file.write(code)
            temp_file = file.name

        result = subprocess.run(
            [sys.executable, temp_file],
            capture_output=True,
            text=True,
            timeout=5
        )

        if result.returncode == 0:
            return result.stdout

        return f"Code Error:\n{result.stderr}"

    except subprocess.TimeoutExpired:
        return "Code execution timed out."

    except Exception as e:
        return f"Execution Error: {e}"

    finally:
        if temp_file and os.path.exists(temp_file):
            os.remove(temp_file)