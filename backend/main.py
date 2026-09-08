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

    # Step 1: Router selects the model
    selected_model = choose_model(request.prompt)

    # Step 2: Send request to selected model
    answer = ask_model(request.prompt, selected_model)

    return {
        "model": selected_model,
        "response": answer
    }