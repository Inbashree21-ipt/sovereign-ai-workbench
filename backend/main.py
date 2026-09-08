from fastapi import FastAPI
from pydantic import BaseModel

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