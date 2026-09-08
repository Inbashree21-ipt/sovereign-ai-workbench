from ollama import chat


def ask_model(prompt: str, model_name: str) -> str:
    response = chat(
        model=model_name,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return response["message"]["content"]