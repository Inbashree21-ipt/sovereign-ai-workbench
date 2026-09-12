import sys
import os
from pathlib import Path
import tempfile

# --------------------------------------------------
# Python Paths
# --------------------------------------------------

sys.path.append(
    os.path.dirname(os.path.abspath(__file__))
)

sys.path.append(
    os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )
)

# --------------------------------------------------
# Imports
# --------------------------------------------------

from fastapi import (
    FastAPI,
    UploadFile,
    File,
    HTTPException
)

from fastapi.middleware.cors import CORSMiddleware

from fastapi.responses import FileResponse

from pydantic import BaseModel

from ollama import chat

import faiss

from ai.ollama_client import ask_model

from router.model_router import choose_model

from agent.core import ReActAgent

from agent.router import ModelRouter

# Member 5 - OCR
from pdf_ocr import extract_pdf_text

# Member 3 - RAG
from rag.rag_pipeline import RAGPipeline

from rag.retrieve import retrieve_top_k

from rag.ingest import ingest_documents


# --------------------------------------------------
# FastAPI Application
# --------------------------------------------------

app = FastAPI()


# --------------------------------------------------
# Project Paths
# --------------------------------------------------

PROJECT_ROOT = (
    Path(__file__).resolve().parent.parent
)

RAG_DATA_DIR = (
    PROJECT_ROOT /
    "rag" /
    "data"
)

VECTORSTORE_DIR = (
    PROJECT_ROOT /
    "rag" /
    "vectorstore"
)

DELIVERABLES_DIR = (
    PROJECT_ROOT /
    "workspace" /
    "deliverables"
)


# --------------------------------------------------
# Create Required Folders
# --------------------------------------------------

RAG_DATA_DIR.mkdir(
    parents=True,
    exist_ok=True
)

DELIVERABLES_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# --------------------------------------------------
# CORS
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
# Request Models
# --------------------------------------------------

class AskRequest(BaseModel):

    prompt: str


class RAGRequest(BaseModel):

    question: str

    top_k: int = 3


# --------------------------------------------------
# RAG Pipeline
# --------------------------------------------------

rag_pipeline = RAGPipeline()


# --------------------------------------------------
# Helper - Reload RAG Pipeline
# --------------------------------------------------

def reload_rag_pipeline():

    global rag_pipeline

    rag_pipeline = RAGPipeline()


# --------------------------------------------------
# Helper - Get FAISS Chunk Count
# --------------------------------------------------

def get_faiss_chunk_count():

    index_path = (
        VECTORSTORE_DIR /
        "index.faiss"
    )

    if not index_path.exists():

        return 0

    try:

        index = faiss.read_index(
            str(index_path)
        )

        return index.ntotal

    except Exception:

        return 0


# ==================================================
# HELPER - DETECT COMPANY / INDUSTRIAL KNOWLEDGE
# ==================================================

def is_knowledge_question(
    prompt: str
) -> bool:

    prompt = (
        prompt
        .lower()
        .strip()
    )

    knowledge_keywords = [

        "finding",

        "inspection",

        "inspection report",

        "pump",

        "pipeline",

        "maintenance",

        "safety",

        "sop",

        "standard operating procedure",

        "equipment",

        "leakage",

        "leak",

        "wall thickness",

        "pressure",

        "vessel",

        "hydro test",

        "hydro-test",

        "corrosion",

        "industrial",

        "engineering",

        "manual",

        "company knowledge",

        "company manual",

        "internal report",

        "internal document",

        "procedure",

        "compliance",

        "shutdown",

        "valve",

        "flange",

        "seal",

        "inspection finding",

        "maintenance report",
    ]

    return any(
        keyword in prompt
        for keyword in knowledge_keywords
    )


# ==================================================
# HOME
# ==================================================

@app.get("/")
def home():

    return {

        "message":
        "Sovereign AI Workbench Backend is running!"

    }


# ==================================================
# MEMBER 1 - NORMAL AI REQUEST
# ==================================================

@app.post("/ask")
def ask_ai(
    request: AskRequest
):

    routing_result = choose_model(
        request.prompt
    )

    selected_task = (
        routing_result["task"]
    )

    selected_model = (
        routing_result["model"]
    )

    answer = ask_model(
        request.prompt,
        selected_model
    )

    return {

        "task":
        selected_task,

        "model":
        selected_model,

        "response":
        answer

    }


# ==================================================
# MEMBER 4 - AGENT
# ==================================================

@app.post("/agent")
def agent_request(
    request: AskRequest
):

    # --------------------------------------------------
    # DIRECT RAG PATH
    # --------------------------------------------------
    #
    # If the user asks about company / industrial
    # knowledge, directly use the RAG pipeline.
    #
    # This prevents the small local LLM from incorrectly
    # choosing list_files or execute_python_code.
    #
    # Example:
    #
    # What was the finding for Pump P-102?
    #
    # -> RAG
    #
    # --------------------------------------------------

    if is_knowledge_question(
        request.prompt
    ):

        try:

            result = rag_pipeline.query(
                request.prompt
            )

            answer = result.get(
                "answer",
                ""
            )

            sources = result.get(
                "sources",
                []
            )

            if answer and answer.strip():

                return {

                    "response":
                    answer,

                    "success":
                    True,

                    "model":
                    "llama3.2:3b",

                    "task":
                    "general",

                    "steps":
                    1,

                    "deliverables":
                    [],

                    "sources":
                    sources

                }

        except Exception as error:

            print(
                f"[AGENT RAG WARNING] {error}"
            )

    # --------------------------------------------------
    # NORMAL MEMBER 4 AGENT
    # --------------------------------------------------

    router = ModelRouter()

    detected_task = (
        router.classify_task_fast(
            request.prompt
        )
    )

    agent = ReActAgent(
        router=router
    )

    result = agent.run(
        request.prompt,
        task_type=detected_task
    )

    return {

        "response":
        result.final_answer,

        "success":
        result.success,

        "model":
        result.model_used,

        "task":
        result.task_type,

        "steps":
        len(result.steps),

        "deliverables":
        result.deliverables

    }


# ==================================================
# MEMBER 4 / 5 - VISION
# ==================================================

@app.post("/vision")
async def analyze_image(

    prompt: str =
    "Describe this image in detail.",

    image: UploadFile =
    File(...)

):

    image_data = (
        await image.read()
    )

    response = chat(

        model="gemma3:4b",

        messages=[

            {

                "role":
                "user",

                "content":
                prompt,

                "images":
                [image_data]

            }

        ]

    )

    return {

        "task":
        "vision",

        "model":
        "gemma3:4b",

        "filename":
        image.filename,

        "response":
        response[
            "message"
        ][
            "content"
        ]

    }


# ==================================================
# MEMBER 5 - OCR
# ==================================================

@app.post("/ocr/extract")
async def extract_ocr_text(
    file: UploadFile = File(...)
):

    # ----------------------------------------------
    # Validate filename
    # ----------------------------------------------

    if not file.filename:

        raise HTTPException(
            status_code=400,
            detail="Filename is required."
        )

    filename = Path(
        file.filename
    ).name

    # ----------------------------------------------
    # Validate PDF
    # ----------------------------------------------

    if not filename.lower().endswith(".pdf"):

        raise HTTPException(
            status_code=400,
            detail="Only PDF files are supported."
        )

    temporary_path = None

    try:

        # ------------------------------------------
        # Create temporary PDF
        # ------------------------------------------

        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=".pdf"
        ) as temporary_file:

            temporary_path = (
                temporary_file.name
            )

            while True:

                chunk = await file.read(
                    1024 * 1024
                )

                if not chunk:

                    break

                temporary_file.write(
                    chunk
                )

        # ------------------------------------------
        # Run Member 5 OCR
        # ------------------------------------------

        extracted_text = (
            extract_pdf_text(
                temporary_path
            )
        )

        # ------------------------------------------
        # Return OCR result
        # ------------------------------------------

        return {

            "success":
            True,

            "filename":
            filename,

            "type":
            "PDF",

            "method":
            "PDF Text Extraction + Tesseract OCR",

            "text":
            extracted_text

        }

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=(
                f"OCR processing failed: "
                f"{error}"
            )
        )

    finally:

        # ------------------------------------------
        # Delete temporary file
        # ------------------------------------------

        if (
            temporary_path
            and
            os.path.exists(
                temporary_path
            )
        ):

            try:

                os.remove(
                    temporary_path
                )

            except Exception:

                pass


# ==================================================
# MEMBER 3 - RAG
# ==================================================

# --------------------------------------------------
# RAG Query
# --------------------------------------------------

@app.post("/rag/query")
def rag_query(
    request: RAGRequest
):

    result = rag_pipeline.query(
        request.question
    )

    return {

        "answer":
        result.get(
            "answer",
            ""
        ),

        "sources":
        result.get(
            "sources",
            []
        )

    }


# --------------------------------------------------
# RAG Search
# --------------------------------------------------

@app.post("/rag/search")
def rag_search(
    request: RAGRequest
):

    top_k = max(
        1,
        min(
            request.top_k,
            20
        )
    )

    results = retrieve_top_k(
        request.question,
        k=top_k
    )

    return {

        "results":
        results

    }


# --------------------------------------------------
# RAG - Upload Document
# --------------------------------------------------

@app.post("/rag/upload")
async def upload_rag_document(
    file: UploadFile = File(...)
):

    if not file.filename:

        raise HTTPException(
            status_code=400,
            detail="Filename is required."
        )

    filename = Path(
        file.filename
    ).name

    if not filename.lower().endswith(".pdf"):

        raise HTTPException(
            status_code=400,
            detail="Only PDF files are supported."
        )

    destination = (
        RAG_DATA_DIR /
        filename
    )

    if destination.exists():

        raise HTTPException(
            status_code=409,
            detail=(
                f"Document '{filename}' "
                "already exists."
            )
        )

    try:

        with open(
            destination,
            "wb"
        ) as buffer:

            while True:

                chunk = await file.read(
                    1024 * 1024
                )

                if not chunk:

                    break

                buffer.write(
                    chunk
                )

    except Exception as error:

        if destination.exists():

            destination.unlink()

        raise HTTPException(
            status_code=500,
            detail=(
                f"Failed to save document: "
                f"{error}"
            )
        )

    try:

        ingestion_result = (
            ingest_documents()
        )

        if not ingestion_result.get(
            "success",
            False
        ):

            if destination.exists():

                destination.unlink()

            raise HTTPException(
                status_code=500,
                detail=(
                    ingestion_result.get(
                        "message",
                        "Document ingestion failed."
                    )
                )
            )

        reload_rag_pipeline()

    except HTTPException:

        raise

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=(
                f"Document ingestion error: "
                f"{error}"
            )
        )

    return {

        "success":
        True,

        "document": {

            "id":
            filename,

            "name":
            filename,

            "type":
            "PDF",

            "category":
            "User Upload",

            "size":
            destination.stat().st_size,

            "status":
            "Indexed"

        },

        "ingestion":
        ingestion_result

    }


# --------------------------------------------------
# RAG - List Documents
# --------------------------------------------------

@app.get("/rag/documents")
def get_rag_documents():

    documents = []

    pdf_files = sorted(
        RAG_DATA_DIR.glob("*.pdf")
    )

    total_chunks = (
        get_faiss_chunk_count()
    )

    for pdf_file in pdf_files:

        stat = pdf_file.stat()

        documents.append({

            "id":
            pdf_file.name,

            "name":
            pdf_file.name,

            "docName":
            pdf_file.name,

            "type":
            "PDF",

            "category":
            "PDF Document",

            "size":
            stat.st_size,

            "uploadDate":
            stat.st_mtime,

            "createdAt":
            stat.st_mtime,

            "status":
            "Indexed",

            "confidence":
            "Local",

            "chunksCount":
            total_chunks

        })

    return {

        "documents":
        documents,

        "totalDocuments":
        len(documents),

        "indexedChunksTotal":
        total_chunks

    }


# --------------------------------------------------
# RAG - Delete Document
# --------------------------------------------------

@app.delete(
    "/rag/documents/{filename}"
)
def delete_rag_document(
    filename: str
):

    safe_filename = Path(
        filename
    ).name

    if safe_filename != filename:

        raise HTTPException(
            status_code=400,
            detail="Invalid filename."
        )

    if not safe_filename.lower().endswith(
        ".pdf"
    ):

        raise HTTPException(
            status_code=400,
            detail="Only PDF documents can be deleted."
        )

    file_path = (
        RAG_DATA_DIR /
        safe_filename
    )

    if not file_path.exists():

        raise HTTPException(
            status_code=404,
            detail="Document not found."
        )

    pdf_files = list(
        RAG_DATA_DIR.glob("*.pdf")
    )

    if len(pdf_files) <= 1:

        raise HTTPException(
            status_code=400,
            detail=(
                "At least one PDF document "
                "must remain in the RAG knowledge base."
            )
        )

    try:

        file_path.unlink()

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=(
                f"Failed to delete document: "
                f"{error}"
            )
        )

    try:

        ingestion_result = (
            ingest_documents()
        )

        if not ingestion_result.get(
            "success",
            False
        ):

            raise HTTPException(
                status_code=500,
                detail=(
                    ingestion_result.get(
                        "message",
                        "FAISS rebuild failed."
                    )
                )
            )

        reload_rag_pipeline()

    except HTTPException:

        raise

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=(
                f"Failed to rebuild RAG index: "
                f"{error}"
            )
        )

    return {

        "success":
        True,

        "deleted":
        safe_filename,

        "ingestion":
        ingestion_result

    }


# --------------------------------------------------
# RAG - Status
# --------------------------------------------------

@app.get("/rag/status")
def rag_status():

    pdf_files = list(
        RAG_DATA_DIR.glob("*.pdf")
    )

    total_chunks = (
        get_faiss_chunk_count()
    )

    return {

        "totalDocuments":
        len(pdf_files),

        "indexedChunksTotal":
        total_chunks,

        "vectorStore":
        "FAISS",

        "embeddingModel":
        "sentence-transformers/all-MiniLM-L6-v2",

        "status":
        "Indexed"

    }


# ==================================================
# GENERATED DELIVERABLES
# ==================================================

@app.get("/deliverables")
def get_deliverables():

    files = []

    if DELIVERABLES_DIR.exists():

        for file in (
            DELIVERABLES_DIR.iterdir()
        ):

            if file.is_file():

                files.append({

                    "name":
                    file.name,

                    "size":
                    file.stat().st_size,

                    "createdAt":
                    file.stat().st_mtime

                })

    return {

        "files":
        files

    }


# --------------------------------------------------
# Download Generated Deliverable
# --------------------------------------------------

@app.get(
    "/deliverables/download/{filename}"
)
def download_deliverable(
    filename: str
):

    file_path = (
        DELIVERABLES_DIR /
        filename
    )

    if (
        not file_path.exists()
        or
        not file_path.is_file()
    ):

        return {

            "error":
            "File not found"

        }

    return FileResponse(

        path=file_path,

        filename=file_path.name

    )


# ==================================================
# INSTALLED LOCAL MODELS
# ==================================================

@app.get("/models")
def get_models():

    try:

        from ollama import list

        response = list()

        models = []

        for model in response.models:

            models.append({

                "name":
                model.model,

                "size":
                model.size

            })

        return {

            "models":
            models

        }

    except Exception as error:

        return {

            "models":
            [],

            "error":
            str(error)

        }