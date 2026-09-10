"""
Safe File Operations for Sovereign Agent
All operations are jailed within the designated workspace.
"""

from pathlib import Path
from typing import Dict, Any
from tools.base import BaseTool, ToolResult
from config import WORKSPACE_DIR


def _resolve_safe_path(rel_path: str) -> Path:
    """Ensure path cannot traverse outside the workspace."""
    clean_p = rel_path.strip().lstrip("/\\")
    resolved = (WORKSPACE_DIR / clean_p).resolve()
    if not str(resolved).startswith(str(WORKSPACE_DIR.resolve())):
        raise PermissionError(f"Access denied: Path '{rel_path}' attempts to escape workspace.")
    return resolved


class ReadFileTool(BaseTool):
    name = "read_file"
    description = "Reads text, markdown, CSV, or log content from a file inside the workspace."
    parameters = {
        "type": "object",
        "properties": {
            "file_path": {
                "type": "string",
                "description": "Relative path of the file to read within the workspace (e.g. 'reports/inspection.txt').",
            }
        },
        "required": ["file_path"],
    }

    def run(self, **kwargs) -> ToolResult:
        file_path_str = kwargs.get("file_path", "")
        try:
            target_path = _resolve_safe_path(file_path_str)
            if not target_path.exists():
                return ToolResult(
                    success=False,
                    output="",
                    error=f"File '{file_path_str}' does not exist in workspace.",
                )
            if target_path.is_dir():
                return ToolResult(
                    success=False,
                    output="",
                    error=f"'{file_path_str}' is a directory, not a file.",
                )

            content = target_path.read_text(encoding="utf-8", errors="replace")
            return ToolResult(
                success=True,
                output=content,
                data={"file_path": str(target_path), "size_bytes": len(content)},
            )
        except Exception as e:
            return ToolResult(success=False, output="", error=f"Failed reading file: {str(e)}")


class WriteFileTool(BaseTool):
    name = "write_file"
    description = "Writes text or data to a file inside the workspace. Creates parent folders if needed."
    parameters = {
        "type": "object",
        "properties": {
            "file_path": {
                "type": "string",
                "description": "Relative path of the file to write within workspace.",
            },
            "content": {
                "type": "string",
                "description": "Content to write into the file.",
            },
        },
        "required": ["file_path", "content"],
    }

    def run(self, **kwargs) -> ToolResult:
        file_path_str = kwargs.get("file_path", "")
        content = kwargs.get("content", "")
        try:
            target_path = _resolve_safe_path(file_path_str)
            target_path.parent.mkdir(parents=True, exist_ok=True)
            target_path.write_text(content, encoding="utf-8")
            return ToolResult(
                success=True,
                output=f"Successfully wrote {len(content)} characters to '{file_path_str}'.",
                data={"file_path": str(target_path), "size_bytes": len(content)},
            )
        except Exception as e:
            return ToolResult(success=False, output="", error=f"Failed writing file: {str(e)}")


class ListFilesTool(BaseTool):
    name = "list_files"
    description = "Lists files and folders inside the workspace or a workspace subfolder."
    parameters = {
        "type": "object",
        "properties": {
            "sub_dir": {
                "type": "string",
                "description": "Optional subfolder relative to workspace (e.g. 'deliverables'). Defaults to root.",
            }
        },
    }

    def run(self, **kwargs) -> ToolResult:
        sub_dir = kwargs.get("sub_dir", "")
        try:
            target_path = _resolve_safe_path(sub_dir) if sub_dir else WORKSPACE_DIR
            if not target_path.exists():
                return ToolResult(success=False, output="", error=f"Folder '{sub_dir}' does not exist.")

            items = []
            for item in target_path.iterdir():
                item_type = "DIR" if item.is_dir() else "FILE"
                size = item.stat().st_size if item.is_file() else 0
                rel = item.relative_to(WORKSPACE_DIR)
                items.append(f"[{item_type}] {rel} ({size} bytes)")

            result_str = "\n".join(items) if items else "[Directory is empty]"
            return ToolResult(success=True, output=result_str, data={"count": len(items)})
        except Exception as e:
            return ToolResult(success=False, output="", error=f"Failed listing files: {str(e)}")
