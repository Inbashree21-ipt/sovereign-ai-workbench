"""
Security and AST Analysis Module for the Code Sandbox
Enforces strict policies:
- No network access (disallow socket, urllib, requests, http, etc.)
- No shell / unauthorized subprocess execution
- No dynamic code execution (eval, exec)
- No unauthorized filesystem traversal
"""

import ast
from typing import List, Tuple
from config import BANNED_MODULES, BANNED_FUNCTIONS


class SecurityViolation(Exception):
    """Raised when user or LLM-generated code violates sandbox safety policies."""
    pass


class CodeSecurityValidator(ast.NodeVisitor):
    """
    AST Visitor to statically inspect Python code before execution in the sandbox.
    """

    def __init__(self):
        self.violations: List[str] = []

    def visit_Import(self, node: ast.Import):
        for alias in node.names:
            base_module = alias.name.split(".")[0]
            if base_module in BANNED_MODULES or alias.name in BANNED_MODULES:
                self.violations.append(
                    f"Forbidden import '{alias.name}' detected (Line {node.lineno}). "
                    f"External networking and subprocess modules are blocked in the sovereign sandbox."
                )
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom):
        if node.module:
            base_module = node.module.split(".")[0]
            if base_module in BANNED_MODULES or node.module in BANNED_MODULES:
                self.violations.append(
                    f"Forbidden import from '{node.module}' detected (Line {node.lineno}). "
                    f"External networking and subprocess modules are blocked in the sovereign sandbox."
                )
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call):
        # Detect calls to banned built-ins (eval, exec, compile, etc.)
        if isinstance(node.func, ast.Name):
            if node.func.id in BANNED_FUNCTIONS:
                self.violations.append(
                    f"Forbidden function call '{node.func.id}()' detected (Line {node.lineno})."
                )
        # Detect os.system, os.popen, os.kill, etc.
        elif isinstance(node.func, ast.Attribute):
            if isinstance(node.func.value, ast.Name) and node.func.value.id == "os":
                if node.func.attr in {"system", "popen", "spawn", "execl", "execv", "kill", "remove", "rmdir"}:
                    self.violations.append(
                        f"Forbidden OS operation 'os.{node.func.attr}()' detected (Line {node.lineno})."
                    )
        self.generic_visit(node)


def validate_python_code(code: str) -> Tuple[bool, List[str]]:
    """
    Statically analyzes code for safety.
    Returns: (is_safe: bool, violations: List[str])
    """
    try:
        tree = ast.parse(code)
    except SyntaxError as e:
        return False, [f"SyntaxError in generated code: {str(e)}"]

    validator = CodeSecurityValidator()
    validator.visit(tree)

    if validator.violations:
        return False, validator.violations
    return True, []
