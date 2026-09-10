import sys
import os

# Add backend folder to Python path
sys.path.append(
    os.path.dirname(os.path.abspath(__file__))
)

# Add project root to Python path
sys.path.append(
    os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )
)

from fastapi import FastAPI, UploadFile, File
from pydantic import BaseModel
from ollama import chat

from ai.ollama_client import ask_model
from router.model_router import choose_model
from agent.core import ReActAgent


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


@app.post("/agent")
def agent_request(request: AskRequest):

    agent = ReActAgent()

    result = agent.run(request.prompt)

    return {
        "response": result.final_answer,
        "success": result.success,
        "model": result.model_used,
        "task": result.task_type,
        "steps": len(result.steps),
        "deliverables": result.deliverables
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