import sys
import os
import re
import logging


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
from planner import create_plan

from tools.file_tool import read_file
from tools.calculator_tool import calculate
from tools.code_tool import run_python_code


# --------------------------------
# Logging Setup
# --------------------------------

LOG_DIR = os.path.join(
    os.path.dirname(__file__),
    "..",
    "logs"
)

os.makedirs(LOG_DIR, exist_ok=True)

LOG_FILE = os.path.join(
    LOG_DIR,
    "agent.log"
)

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


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
    marker = re.search(
        r"Run this Python code:\s*(.*)",
        prompt,
        re.DOTALL | re.IGNORECASE
    )

    if marker:
        return marker.group(1).strip()

    return None

def run_agent(prompt: str):

    logger.info("Agent request received")

    plan = create_plan(prompt)
    logger.info(f"Agent plan created: {plan}")

    results = []

    # --------------------------------
    # Execute Planned Steps
    # --------------------------------

    for step in plan:

        logger.info(f"Executing planned step: {step}")

        # --------------------------------
        # File Tool
        # --------------------------------

        if step == "file":

            file_path = extract_file_path(prompt)

            logger.info(
                f"Reading local file: {file_path}"
            )

            document = read_file(file_path)

            if document == "File not found.":

                logger.warning(
                    f"File not found: {file_path}"
                )

                results.append(
                    f"File not found: {file_path}"
                )

                continue

            if document.startswith("Could not read"):

                logger.error(
                    f"Could not read file: {file_path}"
                )

                results.append(document)

                continue

            full_prompt = f"""
Explain the following local document.

Document:
{document}
"""

            routing_result = choose_model(prompt)

            model = routing_result["model"]

            logger.info(
                f"Local model selected: {model}"
            )

            response = ask_model(
                full_prompt,
                model
            )

            results.append(response)

        # --------------------------------
        # Calculator Tool
        # --------------------------------

        elif step == "calculator":

            logger.info(
                "Running calculator tool"
            )

            response = calculator_tool(prompt)

            results.append(response)

        # --------------------------------
        # Code Tool
        # --------------------------------

        elif step == "code":

            logger.info(
                "Running Python code tool"
            )

            code = extract_code(prompt)

            if code is None:

                response = (
                    "Please provide Python code "
                    "inside a code block."
                )

            else:

                response = run_python_code(code)

            results.append(response)

        # --------------------------------
        # General AI
        # --------------------------------

        elif step == "none":

            logger.info(
                "No tool required"
            )

            routing_result = choose_model(prompt)

            model = routing_result["model"]

            logger.info(
                f"Local model selected: {model}"
            )

            response = ask_model(
                prompt,
                model
            )

            results.append(response)

    # --------------------------------
    # Return Combined Results
    # --------------------------------

    logger.info(
        f"Agent completed {len(plan)} planned step(s)"
    )

    return "\n\n".join(results)

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