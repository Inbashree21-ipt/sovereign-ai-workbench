"""
Central Tool Registry for the Sovereign Agent
"""

from typing import Dict, List, Optional
from tools.base import BaseTool, ToolResult
from tools.code_runner import ExecutePythonTool
from tools.file_ops import ReadFileTool, WriteFileTool, ListFilesTool
from tools.data_analysis import AnalyzeSpreadsheetTool
from tools.rag_search import RAGSearchTool
from tools.doc_generator import GenerateDocumentTool
from tools.egress_monitor import VerifySovereigntyTool


class ToolRegistry:
    """Registry managing available tools and formatting schemas."""

    def __init__(self):
        self._tools: Dict[str, BaseTool] = {}

    def register(self, tool: BaseTool):
        self._tools[tool.name] = tool

    def get(self, name: str) -> Optional[BaseTool]:
        return self._tools.get(name)

    def list_tools(self) -> List[BaseTool]:
        return list(self._tools.values())

    def execute_tool(self, name: str, **kwargs) -> ToolResult:
        tool = self.get(name)
        if not tool:
            return ToolResult(
                success=False,
                output="",
                error=f"Tool '{name}' not found. Available tools: {list(self._tools.keys())}",
            )
        try:
            return tool.run(**kwargs)
        except Exception as e:
            return ToolResult(
                success=False,
                output="",
                error=f"Error executing tool '{name}': {str(e)}",
            )

    def get_schemas(self) -> List[Dict]:
        return [tool.get_schema() for tool in self._tools.values()]

    def format_react_prompt(self) -> str:
        """Formats tools for standard ReAct agent reasoning."""
        lines = []
        for tool in self._tools.values():
            lines.append(tool.format_react_description())
        return "\n\n".join(lines)


def get_default_registry() -> ToolRegistry:
    """Instantiates registry with all standard industrial tools."""
    registry = ToolRegistry()
    registry.register(ExecutePythonTool())
    registry.register(ReadFileTool())
    registry.register(WriteFileTool())
    registry.register(ListFilesTool())
    registry.register(AnalyzeSpreadsheetTool())
    registry.register(RAGSearchTool())
    registry.register(GenerateDocumentTool())
    registry.register(VerifySovereigntyTool())
    return registry
