"""
Base Tool Definitions and Contracts
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from dataclasses import dataclass, field


@dataclass
class ToolResult:
    success: bool
    output: str
    error: Optional[str] = None
    data: Optional[Dict[str, Any]] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "output": self.output,
            "error": self.error,
            "data": self.data or {},
        }

    def __str__(self) -> str:
        if self.success:
            return self.output
        return f"Error: {self.error or self.output}"


class BaseTool(ABC):
    """Abstract Base Class for all Sovereign Agent Tools."""

    name: str
    description: str
    parameters: Dict[str, Any]

    @abstractmethod
    def run(self, **kwargs) -> ToolResult:
        """Execute the tool with given keyword arguments."""
        pass

    def get_schema(self) -> Dict[str, Any]:
        """Returns JSON schema for Ollama / LLM function calling."""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters,
            },
        }

    def format_react_description(self) -> str:
        """Formats tool for ReAct text prompt."""
        props = self.parameters.get("properties", {})
        param_desc = ", ".join([f"{k} ({v.get('type', 'any')}): {v.get('description', '')}" for k, v in props.items()])
        return f"- {self.name}: {self.description}\n  Arguments: {param_desc}"
