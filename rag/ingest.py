import os
import sys

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

# =========================================================
# MEMBER 5 OCR INTEGRATION
# =========================================================

sys.path.insert(
    0,
    os.path.join(
        os.path.dirname(__file__),
        "..",
        "backend"
    )
)

from pdf_ocr import extract_pdf_text


# =========================================================
# PATHS
# =========================================================

DATA_DIR = os.path.join(
    os.path.dirname(__file__),
    "data"
)

VECTORSTORE_DIR = os.path.join(
    os.path.dirname(__file__),
    "vectorstore"
)

EMBEDDING_MODEL = (
    "sentence-transformers/all-MiniLM-L6-v2"
)


# =========================================================
# DOCUMENT INGESTION
# =========================================================

def ingest_documents():

    print(
        "--- Starting Document Ingestion Pipeline ---"
    )

    # =====================================================
    # CHECK DATA DIRECTORY
    # =====================================================

    if not os.path.exists(DATA_DIR):

        message = (
            f"Error: Data directory "
            f"'{DATA_DIR}' does not exist."
        )

        print(message)

        return {
            "success": False,
            "documents": 0,
            "pages": 0,
            "chunks": 0,
            "message": message
        }

    # =====================================================
    # FIND PDF FILES
    # =====================================================

    pdf_files = [
        f
        for f in os.listdir(DATA_DIR)
        if f.lower().endswith(".pdf")
    ]

    if not pdf_files:

        message = (
            f"No PDF files found in "
            f"'{DATA_DIR}'."
        )

        print(message)

        return {
            "success": False,
            "documents": 0,
            "pages": 0,
            "chunks": 0,
            "message": message
        }

    print(
        f"Found {len(pdf_files)} PDF documents "
        f"to process."
    )

    # =====================================================
    # LOAD PDF PAGES
    # =====================================================

    all_pages = []
    documents_loaded = 0

    for pdf_file in pdf_files:

        pdf_path = os.path.join(
            DATA_DIR,
            pdf_file
        )

        print(
            f"\nLoading: {pdf_file}..."
        )

        try:

            # -------------------------------------------------
            # FIRST: NORMAL PDF TEXT EXTRACTION
            # -------------------------------------------------

            loader = PyPDFLoader(pdf_path)

            pages = loader.load()

            # Check whether the PDF actually contains text
            has_text = any(
                page.page_content.strip()
                for page in pages
            )

            # -------------------------------------------------
            # SECOND: OCR FALLBACK
            # -------------------------------------------------

            if has_text:

                print(
                    f"Normal text extraction successful "
                    f"for {pdf_file}"
                )

                all_pages.extend(pages)

            else:

                print(
                    f"No text found in {pdf_file}."
                )

                print(
                    "Using Member 5 Tesseract OCR..."
                )

                ocr_text = extract_pdf_text(
                    pdf_path
                )

                if not ocr_text.strip():

                    print(
                        f"WARNING: OCR returned no text "
                        f"for {pdf_file}.",
                        file=sys.stderr
                    )

                else:

                    # -------------------------------------------------
                    # CREATE A LANGCHAIN DOCUMENT FROM OCR TEXT
                    # -------------------------------------------------

                    from langchain_core.documents import Document

                    ocr_document = Document(
                        page_content=ocr_text,
                        metadata={
                            "source": pdf_path,
                            "page": 0
                        }
                    )

                    all_pages.append(
                        ocr_document
                    )

                    print(
                        f"OCR text successfully extracted "
                        f"from {pdf_file}"
                    )

            documents_loaded += 1

            print(
                f"Successfully processed "
                f"{pdf_file}"
            )

        except Exception as e:

            print(
                f"Error processing {pdf_file}: {e}",
                file=sys.stderr
            )

    # =====================================================
    # CHECK LOADED PAGES
    # =====================================================

    if not all_pages:

        message = (
            "No pages could be extracted. "
            "Exiting ingestion pipeline."
        )

        print(message)

        return {
            "success": False,
            "documents": 0,
            "pages": 0,
            "chunks": 0,
            "message": message
        }

    print(
        f"\nTotal documents loaded: "
        f"{documents_loaded}"
    )

    print(
        f"Total pages processed: "
        f"{len(all_pages)}"
    )

    # =====================================================
    # SPLIT INTO CHUNKS
    # =====================================================

    print(
        "\nSplitting text into chunks..."
    )

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len
    )

    chunks = text_splitter.split_documents(
        all_pages
    )

    print(
        f"Total chunks created: "
        f"{len(chunks)}"
    )

    # =====================================================
    # CHECK CHUNKS
    # =====================================================

    if not chunks:

        message = (
            "No text chunks were created. "
            "Exiting ingestion pipeline."
        )

        print(message)

        return {
            "success": False,
            "documents": documents_loaded,
            "pages": len(all_pages),
            "chunks": 0,
            "message": message
        }

    # =====================================================
    # CREATE EMBEDDINGS + FAISS INDEX
    # =====================================================

    print(
        f"\nInitializing embedding model: "
        f"{EMBEDDING_MODEL}..."
    )

    try:

        embeddings = HuggingFaceEmbeddings(
            model_name=EMBEDDING_MODEL
        )

        print(
            "Generating embeddings and "
            "building FAISS index..."
        )

        db = FAISS.from_documents(
            chunks,
            embeddings
        )

        # =================================================
        # SAVE VECTOR DATABASE
        # =================================================

        print(
            f"Saving FAISS vector database inside: "
            f"{VECTORSTORE_DIR}..."
        )

        os.makedirs(
            VECTORSTORE_DIR,
            exist_ok=True
        )

        db.save_local(
            VECTORSTORE_DIR
        )

        print(
            "Vector database successfully "
            "created and saved locally!"
        )

        # =================================================
        # RETURN INGESTION INFORMATION
        # =================================================

        result = {
            "success": True,
            "documents": documents_loaded,
            "pages": len(all_pages),
            "chunks": len(chunks),
            "vectorstore": VECTORSTORE_DIR,
            "message": (
                "Document ingestion completed successfully."
            )
        }

        print(
            f"\nIngestion complete: "
            f"{documents_loaded} documents, "
            f"{len(all_pages)} pages, "
            f"{len(chunks)} chunks."
        )

        return result

    except Exception as e:

        message = (
            f"Error creating/saving vector database: {e}"
        )

        print(
            message,
            file=sys.stderr
        )

        return {
            "success": False,
            "documents": documents_loaded,
            "pages": len(all_pages),
            "chunks": 0,
            "message": message
        }


# =============================================================
# STANDALONE EXECUTION
# =============================================================

if __name__ == "__main__":

    result = ingest_documents()

    print(
        "\n--- Ingestion Result ---"
    )

    print(result)