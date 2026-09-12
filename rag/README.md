# Member 3 — RAG + Document/PDF Processing Module

This is a standalone, functional Retrieval-Augmented Generation (RAG) system built to parse PDF documentation, index structural semantic text blocks locally, and answer user queries using a localized LLM runtime.

## 🏗️ Architecture Flow
PDF File ➡️ PyPDF Text Extraction ➡️ Text Chunking ➡️ HuggingFace Embeddings ➡️ FAISS Vector Index ➡️ Similarity Retrieval ➡️ Local Ollama Prompt Injection ➡️ Verified Answer Output

---

## 🛠️ Installation & Environment Setup

### 1. Python Virtual Environment Setup
Navigate to the `rag/` root directory and execute:
```bash
# Create environment
python -m venv venv

# Activate on Windows
venv\Scripts\activate

# Activate on macOS/Linux
source venv/bin/activate

# Install required dependencies
pip install -r requirements.txt
```

### 2. Install and Configure Local LLM Engine
1. Download and install Ollama from [ollama.com](https://ollama.com).
2. Start the Ollama desktop manager or daemon runner.
3. Open your terminal and fetch the specific project runtime target:
```bash
ollama pull qwen3:4b
```
4. Verify the model is active locally by typing `ollama list`.

---

## 🚀 Usage Guide

### Step 1: Prepare Your Documents
Place your target PDF files inside the `data/` directory (e.g., `rag/data/sample.pdf`).

### Step 2: Run the Ingestion Pipeline
Execute the processing engine to read, fragment, and transform the textual components into local FAISS vector maps:
```bash
python ingest.py
```
*This will create operational artifacts inside the `vectorstore/` directory (`index.faiss` and `index.pkl`).*

### Step 3: Test Isolated Semantic Search Retrieval
Verify context distance matrices and chunk mapping by running:
```bash
python retrieve.py
```

### Step 4: Run the Complete RAG Pipeline End-to-End
Run the primary script execution pathway to test answering mechanics:
```bash
python rag_pipeline.py
```

---

## 🔌 Backend Integration Blueprint

The `rag_pipeline.py` contains a decoupled class architecture explicitly engineered to be imported by other backend/agent architectures (e.g., Member 1) without rewriting any internal extraction loops.

### Programmatic Integration Example:
```python
from rag.rag_pipeline import RAGPipeline

# Initialize the pipeline core context engine
rag_engine = RAGPipeline()

# Submit queries dynamically from an API gateway or application layer
user_query = "What is the warranty policy outlined in section 4?"
result = rag_engine.query(user_query, k=3)

# Access clean, structured payload responses
print("Answer:", result["answer"])
print("Linked Sources:", result["sources"])
```
