from ollama import chat

image_path = r"C:\Users\inbas\Downloads\portal_login_screenshot.png"

response = chat(
    model="gemma3:4b",
    messages=[
        {
            "role": "user",
            "content": "Describe this image in a few sentences.",
            "images": [image_path]
        }
    ]
)

print(response["message"]["content"])