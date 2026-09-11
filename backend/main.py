import sys
import os
from pathlib import Path

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
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from ollama import chat

from ai.ollama_client import ask_model
from router.model_router import choose_model
from agent.core import ReActAgent


# --------------------------------------------------
# FastAPI Application
# --------------------------------------------------

app = FastAPI()


# --------------------------------------------------
# Deliverables Folder
# --------------------------------------------------

DELIVERABLES_DIR = Path("workspace/deliverables")


# --------------------------------------------------
# CORS - Allow React Frontend
# --------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --------------------------------------------------
# Request Model
# --------------------------------------------------

class AskRequest(BaseModel):
    prompt: str


# --------------------------------------------------
# Home
# --------------------------------------------------

@app.get("/")
def home():
    return {
        "message": "Sovereign AI Workbench Backend is running!"
    }


# --------------------------------------------------
# Normal AI Request
# --------------------------------------------------

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


# --------------------------------------------------
# Agent Request
# --------------------------------------------------

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


# --------------------------------------------------
# Vision Request
# --------------------------------------------------

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


# --------------------------------------------------
# Generated Deliverables
# --------------------------------------------------

@app.get("/deliverables")
def get_deliverables():

    files = []

    if DELIVERABLES_DIR.exists():

        for file in DELIVERABLES_DIR.iterdir():

            if file.is_file():

                files.append({
                    "name": file.name,
                    "size": file.stat().st_size,
                    "createdAt": file.stat().st_mtime
                })

    return {
        "files": files
    }


# --------------------------------------------------
# Download Generated Deliverable
# --------------------------------------------------

@app.get("/deliverables/download/{filename}")
def download_deliverable(filename: str):

    file_path = DELIVERABLES_DIR / filename

    if not file_path.exists() or not file_path.is_file():
        return {
            "error": "File not found"
        }

    return FileResponse(
        path=file_path,
        filename=file_path.name
    )


# --------------------------------------------------
# Installed Local Models
# --------------------------------------------------

@app.get("/models")
def get_models():

    try:
        from ollama import list

        response = list()

        models = []

        for model in response.models:

            models.append({
                "name": model.model,
                "size": model.size
            })

        return {
            "models": models
        }

    except Exception as error:

        return {
            "models": [],
            "error": str(error)
        }