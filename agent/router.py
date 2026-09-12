"""
Multi-Model Router for Sovereign Industrial Workbench
SIH Problem Statement 26117

Routes tasks dynamically to the appropriate local model:
- Coding tasks -> coding model
- Document reasoning / summarization -> reasoning model
- Visual inspection / P&ID -> vision model
- General questions -> general model
"""

import json
import urllib.request
from typing import Dict, Any, Tuple, Optional

from config import MODEL_REGISTRY, DEFAULT_MODEL, OLLAMA_BASE_URL


class ModelRouter:
    """
    Classifies incoming user tasks and routes them
    to the appropriate local model.
    """

    def __init__(
        self,
        registry: Optional[Dict[str, Dict[str, Any]]] = None,
        base_url: str = OLLAMA_BASE_URL
    ):
        self.registry = registry or MODEL_REGISTRY
        self.base_url = base_url
        self._installed_models_cache = None

    # ============================================================
    # GET INSTALLED OLLAMA MODELS
    # ============================================================

    def get_installed_models(self) -> list:
        """Queries local Ollama for downloaded models."""

        try:

            req = urllib.request.Request(
                f"{self.base_url}/api/tags"
            )

            with urllib.request.urlopen(
                req,
                timeout=3
            ) as resp:

                data = json.loads(
                    resp.read().decode("utf-8")
                )

                return [
                    m.get("name")
                    for m in data.get("models", [])
                    if m.get("name")
                ]

        except Exception:

            return [DEFAULT_MODEL]

    # ============================================================
    # FAST TASK CLASSIFICATION
    # ============================================================

    def classify_task_fast(
        self,
        prompt: str
    ) -> str:

        """
        Fast heuristic classification.

        Returns:
            coding
            vision
            reasoning
            general
        """

        p_lower = prompt.lower().strip()

        # --------------------------------------------------------
        # VISION
        # --------------------------------------------------------

        vision_keywords = [
            "image",
            "photo",
            "p&id",
            "drawing",
            "scan",
            "handwritten",
            "schematic",
            "ocr",
            "picture",
            "screenshot",
            "visual",
            "diagram"
        ]

        if any(
            word in p_lower
            for word in vision_keywords
        ):

            return "vision"

        # --------------------------------------------------------
        # CODING
        # --------------------------------------------------------
        #
        # IMPORTANT:
        # Do NOT use "python" alone as a coding keyword.
        #
        # Example:
        # "What is Python?"
        # -> general
        #
        # But:
        # "Write a Python program"
        # -> coding
        #
        # --------------------------------------------------------

        coding_keywords = [
            "write code",
            "write a program",
            "create a program",
            "generate code",
            "python program",
            "python code",
            "java program",
            "java code",
            "c program",
            "c++ program",
            "javascript code",
            "javascript program",
            "code for",
            "program for",
            "coding",
            "script",
            "calculate",
            "calculate using code",
            "sum using python",
            "math using python",
            "validate spreadsheet",
            "totals",
            "regex",
            "algorithm",
            "debug",
            "debug this",
            "fix this code",
            "execute code",
            "run code",
            "sandbox"
        ]

        if any(
            word in p_lower
            for word in coding_keywords
        ):

            return "coding"

        # --------------------------------------------------------
        # REASONING / DOCUMENT TASKS
        # --------------------------------------------------------

        reasoning_keywords = [
            "approval note",
            "memo",
            "compliance",
            "sop",
            "standard operating",
            "regulation",
            "summarize report",
            "summarise report",
            "summarize document",
            "summarise document",
            "summary of report",
            "summary of document",
            "policy",
            "investigation",
            "analyze report",
            "analyse report",
            "review report",
            "explain report",
            "explain document"
        ]

        if any(
            word in p_lower
            for word in reasoning_keywords
        ):

            return "reasoning"

        # --------------------------------------------------------
        # GENERAL
        # --------------------------------------------------------

        return "general"

    # ============================================================
    # OPTIONAL LLM CLASSIFIER
    # ============================================================

    def classify_with_llm(
        self,
        prompt: str,
        classifier_model: Optional[str] = None
    ) -> str:

        """
        Optional lightweight LLM classifier.

        Used only when explicitly called.
        """

        model = (
            classifier_model
            or DEFAULT_MODEL
        )

        classify_prompt = (
            "You are a fast task classifier for an "
            "industrial AI workbench.\n"
            "Classify the following user prompt into "
            "exactly ONE category from: "
            "[CODING, REASONING, VISION, GENERAL].\n"
            "A question asking what a programming language "
            "is should be GENERAL unless the user asks "
            "to write, debug, execute, or modify code.\n"
            "Respond ONLY with the category word "
            "in uppercase and nothing else.\n\n"
            f"Prompt: {prompt[:300]}\n\n"
            "Category:"
        )

        try:

            payload = json.dumps(
                {
                    "model": model,
                    "prompt": classify_prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.0,
                        "num_predict": 10
                    },
                }
            ).encode("utf-8")

            req = urllib.request.Request(
                f"{self.base_url}/api/generate",
                data=payload,
                headers={
                    "Content-Type": "application/json"
                },
            )

            with urllib.request.urlopen(
                req,
                timeout=5
            ) as resp:

                data = json.loads(
                    resp.read().decode("utf-8")
                )

                raw_cat = (
                    data
                    .get("response", "")
                    .strip()
                    .upper()
                )

                for category in [
                    "CODING",
                    "REASONING",
                    "VISION",
                    "GENERAL"
                ]:

                    if category in raw_cat:

                        return category.lower()

        except Exception:

            pass

        return self.classify_task_fast(
            prompt
        )

    # ============================================================
    # ROUTE TASK
    # ============================================================

    def route(
        self,
        prompt: str,
        task_type: Optional[str] = None
    ) -> Tuple[
        str,
        str,
        Dict[str, Any]
    ]:

        """
        Routes task to:

        (
            selected_model,
            endpoint,
            metadata
        )
        """

        # --------------------------------------------------------
        # Classify task
        # --------------------------------------------------------

        if not task_type:

            task_type = (
                self.classify_task_fast(
                    prompt
                )
            )

        # --------------------------------------------------------
        # Get model configuration
        # --------------------------------------------------------

        spec = self.registry.get(
            task_type,
            self.registry["general"]
        )

        desired_model = spec.get(
            "model",
            DEFAULT_MODEL
        )

        endpoint = spec.get(
            "endpoint",
            self.base_url
        )

        # --------------------------------------------------------
        # Check installed models
        # --------------------------------------------------------

        installed = (
            self.get_installed_models()
        )

        chosen_model = desired_model

        model_base_names = [
            m.split(":")[0]
            for m in installed
        ]

        desired_base = (
            desired_model.split(":")[0]
        )

        # --------------------------------------------------------
        # Fallback if model isn't installed
        # --------------------------------------------------------

        if (
            desired_model not in installed
            and
            desired_base not in model_base_names
        ):

            chosen_model = (
                installed[0]
                if installed
                else DEFAULT_MODEL
            )

        # --------------------------------------------------------
        # Routing metadata
        # --------------------------------------------------------

        metadata = {

            "task_type":
            task_type,

            "desired_model":
            desired_model,

            "routed_model":
            chosen_model,

            "endpoint":
            endpoint,

            "description":
            spec.get(
                "description",
                ""
            ),

            "is_fallback":
            (
                chosen_model !=
                desired_model
            )

        }

        return (
            chosen_model,
            endpoint,
            metadata
        )