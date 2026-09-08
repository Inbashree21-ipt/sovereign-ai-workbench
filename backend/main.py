from fastapi import FastAPI, UploadFile, File
from pydantic import BaseModel
from ollama import chat

from ai.ollama_client import ask_model
from router.model_router import choose_model


app = FastAPI()


class AskRequest(BaseModel):
    prompt: str


@app.get("/")
def home():
    return {
        "message": "Sovereign AI Workbench Backend is running!"
    }


@app.post("/ask")
def ask_ai(request: AskRequest):

    routing_result = choose_model(request.prompt)

    selected_task = routing_result["task"]
    selected_model = routing_result["model"]

    answer = ask_model(
        request.prompt,
        selected_model
    )

    return {
        "task": selected_task,
        "model": selected_model,
        "response": answer
    }


@app.post("/vision")
async def analyze_image(
    prompt: str = "Describe this image in detail.",
    image: UploadFile = File(...)
):

    image_data = await image.read()

    response = chat(
        model="gemma3:4b",
        messages=[
            {
                "role": "user",
                "content": prompt,
                "images": [image_data]
            }
        ]
    )

    return {
        "task": "vision",
        "model": "gemma3:4b",
        "filename": image.filename,
        "response": response["message"]["content"]
    }