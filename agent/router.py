"""
Multi-Model Router for Sovereign Industrial Workbench
Fulfills SIH Problem Statement 26117 Part 4: 'Multi-model routing (not locked to one model)'
Routes tasks dynamically to the best local open-weight model:
- Coding tasks -> coding model (e.g. qwen2.5-coder:7b or active local model)
- Document reasoning / summarization -> reasoning model (e.g. qwen2.5:14b or active local model)
- Visual inspection / P&ID -> vision model (e.g. llama3.2-vision:11b)
- General workflow -> general model
"""

import re
import json
import urllib.request
from typing import Dict, Any, Tuple, Optional
from config import MODEL_REGISTRY, DEFAULT_MODEL, OLLAMA_BASE_URL


class ModelRouter:
    """
    Classifies incoming user tasks and routes them to the appropriate local model endpoint.
    Designed for zero-rearchitecting extensibility: adding a model is 1 dictionary line.
    """

    def __init__(self, registry: Optional[Dict[str, Dict[str, Any]]] = None, base_url: str = OLLAMA_BASE_URL):
        self.registry = registry or MODEL_REGISTRY
        self.base_url = base_url
        self._installed_models_cache = None

    def get_installed_models(self) -> list:
        """Queries local Ollama to find what models are currently downloaded."""
        try:
            req = urllib.request.Request(f"{self.base_url}/api/tags")
            with urllib.request.urlopen(req, timeout=3) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                return [m.get("name") for m in data.get("models", [])]
        except Exception:
            return [DEFAULT_MODEL]

    def classify_task_fast(self, prompt: str) -> str:
        """
        Fast heuristic classification based on keyword signals.
        Returns: 'coding', 'vision', 'reasoning', or 'general'.
        """
        p_lower = prompt.lower()

        # Vision signals
        if any(w in p_lower for w in ["image", "photo", "p&id", "drawing", "scan", "handwritten", "schematic", "ocr"]):
            return "vision"

        # Coding / Calculation / Scripting signals
        if any(w in p_lower for w in ["code", "python", "script", "calculate", "sum", "math", "validate spreadsheet", "totals", "regex", "algorithm", "debug", "sandbox"]):
            return "coding"

        # Deep reasoning / Document drafting signals
        if any(w in p_lower for w in ["approval note", "memo", "compliance", "sop", "standard operating", "regulation", "summarize report", "policy", "investigation"]):
            return "reasoning"

        return "general"

    def classify_with_llm(self, prompt: str, classifier_model: Optional[str] = None) -> str:
        """
        Optional lightweight LLM classifier pass (as described in SIH brief Part 4).
        """
        model = classifier_model or DEFAULT_MODEL
        classify_prompt = (
            "You are a fast task classifier for an industrial AI workbench.\n"
            "Classify the following user prompt into exactly ONE category from: [CODING, REASONING, VISION, GENERAL].\n"
            "Respond ONLY with the category word in uppercase and nothing else.\n\n"
            f"Prompt: {prompt[:300]}\n\n"
            "Category:"
        )

        try:
            payload = json.dumps({
                "model": model,
                "prompt": classify_prompt,
                "stream": False,
                "options": {"temperature": 0.0, "num_predict": 10},
            }).encode("utf-8")

            req = urllib.request.Request(
                f"{self.base_url}/api/generate",
                data=payload,
                headers={"Content-Type": "application/json"},
            )
            with urllib.request.urlopen(req, timeout=5) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                raw_cat = data.get("response", "").strip().upper()
                for cat in ["CODING", "REASONING", "VISION", "GENERAL"]:
                    if cat in raw_cat:
                        return cat.lower()
        except Exception:
            pass

        # Fallback to fast heuristic if LLM call times out or errors
        return self.classify_task_fast(prompt)

    def route(self, prompt: str, task_type: Optional[str] = None) -> Tuple[str, str, Dict[str, Any]]:
        """
        Routes the task to (target_model, target_endpoint, metadata).
        Guarantees fallback if the specialized model is not yet pulled into Ollama.
        """
        if not task_type:
            task_type = self.classify_task_fast(prompt)

        spec = self.registry.get(task_type, self.registry["general"])
        desired_model = spec.get("model", DEFAULT_MODEL)
        endpoint = spec.get("endpoint", self.base_url)

        # Check if desired model is installed, fallback if not
        installed = self.get_installed_models()
        chosen_model = desired_model

        # If desired_model not in installed list (or without tag), check fallback
        model_base_names = [m.split(":")[0] for m in installed]
        desired_base = desired_model.split(":")[0]

        if desired_model not in installed and desired_base not in model_base_names:
            # Fall back to default installed model
            chosen_model = installed[0] if installed else DEFAULT_MODEL

        metadata = {
            "task_type": task_type,
            "desired_model": desired_model,
            "routed_model": chosen_model,
            "endpoint": endpoint,
            "description": spec.get("description", ""),
            "is_fallback": (chosen_model != desired_model),
        }

        return chosen_model, endpoint, metadata
