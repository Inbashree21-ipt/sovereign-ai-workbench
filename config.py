import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent

WORKSPACE_DIR = PROJECT_ROOT / "workspace"
SANDBOX_DIR = WORKSPACE_DIR / "sandbox"
DELIVERABLES_DIR = WORKSPACE_DIR / "deliverables"

WORKSPACE_DIR.mkdir(parents=True, exist_ok=True)
SANDBOX_DIR.mkdir(parents=True, exist_ok=True)
DELIVERABLES_DIR.mkdir(parents=True, exist_ok=True)


OLLAMA_BASE_URL = os.environ.get(
    "OLLAMA_BASE_URL",
    "http://localhost:11434"
)


DEFAULT_MODEL = os.environ.get(
    "DEFAULT_MODEL",
    "llama3.2:3b"
)


MODEL_REGISTRY = {

    "coding": {
        "endpoint": OLLAMA_BASE_URL,
        "model": os.environ.get(
            "CODING_MODEL",
            "qwen2.5-coder:3b"
        ),
        "fallback_model": "llama3.2:3b",
        "description": "Specialized for Python, programming, debugging and computation"
    },

    "reasoning": {
        "endpoint": OLLAMA_BASE_URL,
        "model": os.environ.get(
            "REASONING_MODEL",
            "llama3.2:3b"
        ),
        "fallback_model": "llama3.2:3b",
        "description": "General reasoning, document summarization and multi-step planning"
    },

    "vision": {
        "endpoint": OLLAMA_BASE_URL,
        "model": os.environ.get(
            "VISION_MODEL",
            "gemma3:4b"
        ),
        "fallback_model": "gemma3:4b",
        "description": "Image, scanned document and visual understanding"
    },

    "general": {
        "endpoint": OLLAMA_BASE_URL,
        "model": DEFAULT_MODEL,
        "fallback_model": "llama3.2:3b",
        "description": "General ReAct orchestration and tool invocation"
    }
}


SANDBOX_TIMEOUT_SECONDS = 15.0

SANDBOX_MAX_OUTPUT_BYTES = 50 * 1024


BANNED_MODULES = {
    "subprocess",
    "socket",
    "requests",
    "urllib",
    "http",
    "ftplib",
    "telnetlib"
}


BANNED_FUNCTIONS = {
    "eval",
    "exec",
    "breakpoint",
    "compile"
}


MAX_AGENT_STEPS = 10