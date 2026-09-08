MODEL_MAP = {
    "coding": "qwen2.5-coder:3b",
    "general": "llama3.2:3b",
    "vision": "llama3.2:3b"
}


def choose_model(prompt: str):

    prompt = prompt.lower()

    coding_keywords = [
        "code",
        "python",
        "java",
        "program",
        "debug",
        "function"
    ]

    document_keywords = [
        "summary",
        "summarize",
        "document",
        "report",
        "explain",
        "letter"
    ]

    vision_keywords = [
        "image",
        "photo",
        "drawing",
        "scan",
        "picture"
    ]

    if any(word in prompt for word in coding_keywords):
        return {
            "task": "coding",
            "model": MODEL_MAP["coding"]
        }

    if any(word in prompt for word in document_keywords):
        return {
            "task": "general",
            "model": MODEL_MAP["general"]
        }

    if any(word in prompt for word in vision_keywords):
        return {
            "task": "vision",
            "model": MODEL_MAP["vision"]
        }

    return {
        "task": "general",
        "model": MODEL_MAP["general"]
    }