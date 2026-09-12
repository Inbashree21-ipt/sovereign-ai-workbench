import os
import sys
from typing import Dict, Any

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_ollama import OllamaLLM
from langchain_core.prompts import PromptTemplate


VECTORSTORE_DIR = os.path.join(os.path.dirname(__file__), "vectorstore")
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
LLM_MODEL = "llama3.2:3b"


class RAGPipeline:
    def __init__(self):
        self.embeddings = HuggingFaceEmbeddings(
            model_name=EMBEDDING_MODEL
        )
        self.db = None
        self.llm = None

        # Enforce strict system parameters to block hallucinations
        self.prompt_template = PromptTemplate.from_template(
            "You are an AI assistant designed to answer questions accurately based only on the provided context.\n"
            "Answer the question using ONLY the supplied document context. Do not invent information.\n"
            "If the answer is not present in the retrieved context, say exactly: "
            "'The information could not be found in the provided documents.'\n"
            "Keep the answer clear, objective, and useful.\n\n"
            "CONTEXT:\n{context}\n\n"
            "QUESTION: {question}\n\n"
            "ANSWER:"
        )

    def _load_vectorstore(self) -> bool:
        if self.db is not None:
            return True

        if not os.path.exists(
            os.path.join(VECTORSTORE_DIR, "index.faiss")
        ):
            print(
                f"Error: FAISS vectorstore not found at "
                f"'{VECTORSTORE_DIR}'. Run ingestion script first.",
                file=sys.stderr
            )
            return False

        try:
            self.db = FAISS.load_local(
                VECTORSTORE_DIR,
                self.embeddings,
                allow_dangerous_deserialization=True
            )
            return True

        except Exception as e:
            print(
                f"Error loading FAISS vector database: {e}",
                file=sys.stderr
            )
            return False

    def _initialize_llm(self) -> bool:
        if self.llm is not None:
            return True

        try:
            # Connect locally through LangChain Ollama driver
            self.llm = OllamaLLM(
                model=LLM_MODEL,
                temperature=0.0
            )
            return True

        except Exception as e:
            print(
                f"Error connecting to Ollama service or loading model "
                f"'{LLM_MODEL}': {e}",
                file=sys.stderr
            )
            return False

    def query(
        self,
        question: str,
        k: int = 3
    ) -> Dict[str, Any]:

        response = {
            "answer": (
                "The information could not be found "
                "in the provided documents."
            ),
            "sources": []
        }

        if not self._load_vectorstore():
            response["answer"] = (
                "Error: Vectorstore initialization failed."
            )
            return response

        try:
            # Retrieve the most relevant document chunks
            docs = self.db.similarity_search(
                question,
                k=k
            )

            if not docs:
                return response

            context_blocks = []
            seen_sources = set()

            # Collect document context and source information
            for doc in docs:
                context_blocks.append(doc.page_content)

                source_path = doc.metadata.get(
                    "source",
                    "Unknown"
                )

                filename = os.path.basename(source_path)

                page = doc.metadata.get(
                    "page",
                    0
                ) + 1

                source_key = (
                    f"{filename}_page_{page}"
                )

                if source_key not in seen_sources:
                    seen_sources.add(source_key)

                    response["sources"].append({
                        "document": filename,
                        "page": page
                    })

            combined_context = (
                "\n\n---\n\n".join(context_blocks)
            )

            # Generate answer using local Ollama model
            if self._initialize_llm():

                full_prompt = self.prompt_template.format(
                    context=combined_context,
                    question=question
                )

                generated_answer = self.llm.invoke(
                    full_prompt
                )

                response["answer"] = (
                    generated_answer.strip()
                )

            else:
                response["answer"] = (
                    "Error: Failed to connect to Ollama "
                    "local runtime engine."
                )

        except Exception as e:
            print(
                f"Exception encountered during pipeline "
                f"processing: {e}",
                file=sys.stderr
            )

            response["answer"] = (
                f"Runtime pipeline error: {str(e)}"
            )

        return response


if __name__ == "__main__":

    pipeline = RAGPipeline()

    print(
        "--- RAG Standalone Pipeline Test CLI ---"
    )

    test_q = input(
        "Enter your pipeline test question: "
    ) or "Summarize the key information."

    res = pipeline.query(test_q)

    print(
        "\n[PIPELINE OUTPUT RESULT]"
    )

    print(
        f"Answer: {res['answer']}"
    )

    print(
        f"Sources: {res['sources']}"
    )

