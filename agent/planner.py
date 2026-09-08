def create_plan(prompt: str):

    prompt = prompt.lower()

    steps = []

    # Detect file reading
    if any(word in prompt for word in [
        "read file",
        "read the file",
        "read document",
        "read the document"
    ]):
        steps.append("file")

    # Detect calculation
    if any(word in prompt for word in [
        "calculate",
        "add",
        "subtract",
        "multiply",
        "divide"
    ]):
        steps.append("calculator")

    # Detect Python execution
    if any(word in prompt for word in [
        "run code",
        "execute code",
        "run python",
        "execute python"
    ]):
        steps.append("code")

    # If nothing was detected
    if not steps:
        steps.append("none")

    return steps