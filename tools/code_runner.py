"""
Code Execution Tool for ReAct Agent
Runs Python code inside the isolated sovereign sandbox.
"""

from typing import Dict, Any
from tools.base import BaseTool, ToolResult
from sandbox.executor import CodeSandbox


class ExecutePythonTool(BaseTool):
    name = "execute_python_code"
    description = (
        "Executes Python code inside an isolated, air-gapped sandbox with zero network access. "
        "Use this for calculations, data validation, parsing, and verifying algorithms. "
        "Prints to stdout are captured and returned."
    )
    parameters = {
        "type": "object",
        "properties": {
            "code": {
                "type": "string",
                "description": "The complete Python script or snippet to execute.",
            }
        },
        "required": ["code"],
    }

    def __init__(self, sandbox: CodeSandbox = None):
        self.sandbox = sandbox or CodeSandbox()

    def run(self, **kwargs) -> ToolResult:
        code = kwargs.get("code", "")
        if not code or not code.strip():
            return ToolResult(
                success=False,
                output="",
                error="No code provided for execution.",
            )

        exec_res = self.sandbox.execute(code)

        if not exec_res.is_success:
            err_msg = exec_res.stderr or f"Execution failed with exit code {exec_res.exit_code}"
            return ToolResult(
                success=False,
                output=exec_res.stdout,
                error=err_msg,
                data=exec_res.to_dict(),
            )

        output_str = exec_res.stdout
        if not output_str.strip():
            output_str = "[Code executed successfully with no stdout output]"

        return ToolResult(
            success=True,
            output=output_str,
            data=exec_res.to_dict(),
        )
