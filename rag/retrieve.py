import os
import sys

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS


VECTORSTORE_DIR = os.path.join(
    os.path.dirname(__file__),
    "vectorstore"
)

EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"


def retrieve_top_k(query: str, k: int = 3):

    print(
        f"\n--- Executing Similarity Search for Query: '{query}' ---"
    )

    index_path = os.path.join(
        VECTORSTORE_DIR,
        "index.faiss"
    )

    if not os.path.exists(index_path):

        print(
            f"Error: FAISS index not found at '{VECTORSTORE_DIR}'. "
            "Run ingest.py first."
        )

        return []


    try:

        # Load embedding model
        embeddings = HuggingFaceEmbeddings(
            model_name=EMBEDDING_MODEL
        )

        # Load FAISS database
        db = FAISS.load_local(
            VECTORSTORE_DIR,
            embeddings,
            allow_dangerous_deserialization=True
        )

        # Retrieve documents with similarity distance
        docs_and_scores = db.similarity_search_with_score(
            query,
            k=k
        )

        results = []

        print(
            f"Retrieved Top-{len(docs_and_scores)} relevant chunks:"
        )

        for idx, (doc, score) in enumerate(
            docs_and_scores,
            start=1
        ):

            source = doc.metadata.get(
                "source",
                "Unknown"
            )

            filename = os.path.basename(source)

            page = doc.metadata.get(
                "page",
                0
            ) + 1

            chunk_text = doc.page_content.strip()

            print(
                f"\n[Chunk {idx}] "
                f"(Distance Score: {score:.4f})"
            )

            print(
                f"Source Document: {filename}"
            )

            print(
                f"Page Number: {page}"
            )

            print(
                f"Content: {chunk_text[:200]}..."
            )

            print("-" * 50)


            results.append({

                "id": idx,

                "docName": filename,

                "page": page,

                "distance": float(score),

                "chunkText": chunk_text

            })


        return results


    except Exception as e:

        print(
            f"Error retrieving documents: {e}",
            file=sys.stderr
        )

        return []


if __name__ == "__main__":

    test_query = input(
        "Enter a user question to test retrieval: "
    ) or "What is the summary of this document?"

    results = retrieve_top_k(
        test_query
    )

    print("\nFinal Retrieved Results:")

    for result in results:

        print(result)