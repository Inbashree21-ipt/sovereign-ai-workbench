import sys
import os
import re


# Add backend folder to Python path
sys.path.append(
    os.path.join(
        os.path.dirname(__file__),
        "..",
        "backend"
    )
)

# Add agent folder to Python path
sys.path.append(
    os.path.dirname(__file__)
)


from ai.ollama_client import ask_model
from router.model_router import choose_model

from tools.file_tool import read_file
from tools.calculator_tool import calculate
from tools.code_tool import run_python_code


def select_tool(prompt: str):

    prompt = prompt.lower()

    # File tool
    if any(word in prompt for word in [
        "file",
        "document",
        "read"
    ]):
        return "file"

    # Calculator tool
    if any(word in prompt for word in [
        "calculate",
        "add",
        "subtract",
        "multiply",
        "divide"
    ]):
        return "calculator"

    # Code tool
    if any(word in prompt for word in [
        "run code",
        "execute code",
        "python code",
        "execute python",
        "run python"
    ]):
        return "code"

    # No tool
    return "none"


def extract_file_path(prompt: str):

    match = re.search(
        r'[\w./\\-]+\.(?:txt|md|csv|json)',
        prompt,
        re.IGNORECASE
    )

    if match:
        return match.group(0)

    return "test.txt"


def calculator_tool(prompt: str):

    numbers = re.findall(
        r"\d+(?:\.\d+)?",
        prompt
    )

    if len(numbers) < 2:
        return "Please provide two numbers."

    a = float(numbers[0])
    b = float(numbers[1])

    prompt = prompt.lower()

    if "+" in prompt or "add" in prompt:
        operation = "add"

    elif "-" in prompt or "subtract" in prompt:
        operation = "subtract"

    elif "*" in prompt or "multiply" in prompt:
        operation = "multiply"

    elif "/" in prompt or "divide" in prompt:
        operation = "divide"

    else:
        return "I could not determine the calculation operation."

    result = calculate(
        a,
        b,
        operation
    )

    return f"The calculation result is: {result}"


def extract_code(prompt: str):

    # Extract Python code from Python code block
    match = re.search(
        r"```python\s*(.*?)```",
        prompt,
        re.DOTALL | re.IGNORECASE
    )

    if match:
        return match.group(1)

    # Extract code from generic code block
    match = re.search(
        r"```\s*(.*?)```",
        prompt,
        re.DOTALL
    )

    if match:
        return match.group(1)

    # Handle plain Python code
    # Example:
    # Run this Python code:
    # print(10 + 20)

    marker = re.search(
        r"Run this Python code:\s*(.*)",
        prompt,
        re.DOTALL | re.IGNORECASE
    )

    if marker:
        return marker.group(1).strip()

    return None


def run_agent(prompt: str):

    tool = select_tool(prompt)

    # --------------------------------
    # File Tool
    # --------------------------------

    if tool == "file":

        file_path = extract_file_path(prompt)

        document = read_file(file_path)

        if document == "File not found.":
            return f"File not found: {file_path}"

        if document.startswith("Could not read"):
            return document

        full_prompt = f"""
Explain the following local document.

Document:
{document}
"""

        routing_result = choose_model(prompt)

        model = routing_result["model"]

        return ask_model(
            full_prompt,
            model
        )

    # --------------------------------
    # Calculator Tool
    # --------------------------------

    elif tool == "calculator":

        return calculator_tool(prompt)

    # --------------------------------
    # Code Tool
    # --------------------------------

    elif tool == "code":

        code = extract_code(prompt)

        if code is None:
            return "Please provide Python code inside a code block."

        return run_python_code(code)

    # --------------------------------
    # General AI
    # --------------------------------

    else:

        routing_result = choose_model(prompt)

        model = routing_result["model"]

        return ask_model(
            prompt,
            model
        )


# --------------------------------
# Local Testing
# --------------------------------

if __name__ == "__main__":

    print("Test 1: File Tool")

    print(
        run_agent(
            "Read the file and explain it."
        )
    )


    print("\nTest 2: Calculator Tool")

    print(
        run_agent(
            "Calculate 25 + 15"
        )
    )


    print("\nTest 3: Code Tool")

    code_request = """
Run this Python code:

numbers = [10, 20, 30]
print(sum(numbers))
"""

    print(
        run_agent(
            code_request
        )
    )


    print("\nTest 4: General AI")

    print(
        run_agent(
            "What is artificial intelligence?"
        )
    )