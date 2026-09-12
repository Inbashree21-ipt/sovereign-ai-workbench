MODEL_MAP = {
    "coding": "qwen2.5-coder:3b",
    "general": "llama3.2:3b",
    "vision": "gemma3:4b"
}


CODING_KEYWORDS = [
    "code",
    "java",
    "program",
    "debug",
    "function",
    "algorithm",
    "programming"
]


VISION_KEYWORDS = [
    "image",
    "photo",
    "drawing",
    "scan",
    "picture",
    "screenshot",
    "visual",
    "diagram"
]


DOCUMENT_KEYWORDS = [
    "summary",
    "summarize",
    "document",
    "report",
    "explain",
    "letter",
    "manual",
    "approval note"
]


def choose_model(prompt: str):

    prompt = prompt.lower().strip()

    # Check coding task
    if any(word in prompt for word in CODING_KEYWORDS):
        return {
            "task": "coding",
            "model": MODEL_MAP["coding"]
        }

    # Check vision task
    if any(word in prompt for word in VISION_KEYWORDS):
        return {
            "task": "vision",
            "model": MODEL_MAP["vision"]
        }

    # Check document/general task
    if any(word in prompt for word in DOCUMENT_KEYWORDS):
        return {
            "task": "general",
            "model": MODEL_MAP["general"]
        }

    # Default model
    return {
        "task": "general",
        "model": MODEL_MAP["general"]
    }