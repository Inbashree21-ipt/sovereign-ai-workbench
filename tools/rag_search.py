"""
RAG Search Tool (Bridge for Member 3's Knowledge Base)

Allows the Agent to query internal industrial SOPs, manuals,
engineering standards, and past maintenance reports.

Features:
1. Pluggable adapter for Member 3's FAISS/embedding retriever.
2. Built-in local keyword search fallback.
3. Runs completely locally inside the workspace.
"""

import math
import re
from typing import Dict, Any, List, Optional, Callable

from tools.base import BaseTool, ToolResult
from config import WORKSPACE_DIR


# =========================================================
# KNOWLEDGE BASE DIRECTORY
# =========================================================

KNOWLEDGE_DIR = WORKSPACE_DIR / "knowledge"
KNOWLEDGE_DIR.mkdir(parents=True, exist_ok=True)


# =========================================================
# RAG SEARCH TOOL
# =========================================================

class RAGSearchTool(BaseTool):

    name = "search_company_knowledge"

    description = (
        "Searches confidential company manuals, engineering standards, "
        "inspection SOPs, and maintenance reports to ground decisions "
        "in enterprise knowledge."
    )

    parameters = {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": (
                    "Search query or topic to find relevant information "
                    "from the internal knowledge base."
                ),
            },
            "top_k": {
                "type": "integer",
                "description": (
                    "Number of relevant knowledge chunks to retrieve. "
                    "Default is 3."
                ),
            },
        },
        "required": ["query"],
    }

    def __init__(
        self,
        external_retriever: Optional[
            Callable[[str, int], List[Dict[str, Any]]]
        ] = None,
    ):
        """
        Optional external retriever.

        Member 3 can later connect their FAISS/vector database
        retriever through this callback.
        """
        self.external_retriever = external_retriever

    # =====================================================
    # REGISTER EXTERNAL RETRIEVER
    # =====================================================

    def register_external_retriever(
        self,
        retriever_fn: Callable[[str, int], List[Dict[str, Any]]],
    ):
        """
        Allows Member 3 to connect their FAISS/vector retriever.
        """
        self.external_retriever = retriever_fn

    # =====================================================
    # LOCAL FALLBACK SEARCH
    # =====================================================

    def _fallback_local_search(
        self,
        query: str,
        top_k: int = 3,
    ) -> List[Dict[str, Any]]:

        query_words = set(
            re.findall(r"\w+", query.lower())
        )

        if not query_words:
            return []

        doc_chunks: List[Dict[str, Any]] = []

        # Search files inside workspace/knowledge
        for doc_file in KNOWLEDGE_DIR.rglob("*"):

            if not doc_file.is_file():
                continue

            if doc_file.suffix.lower() not in [
                ".txt",
                ".md",
                ".json",
                ".csv",
            ]:
                continue

            try:
                text = doc_file.read_text(
                    encoding="utf-8",
                    errors="replace",
                )

                # Split document into paragraphs
                paragraphs = [
                    paragraph.strip()
                    for paragraph in text.split("\n\n")
                    if len(paragraph.strip()) > 30
                ]

                for index, paragraph in enumerate(paragraphs):

                    doc_chunks.append(
                        {
                            "source": doc_file.name,
                            "chunk_id": (
                                f"{doc_file.name}#chunk_{index}"
                            ),
                            "content": paragraph,
                        }
                    )

            except Exception:
                continue

        if not doc_chunks:
            return []

        # =================================================
        # SCORE DOCUMENT CHUNKS
        # =================================================

        scored = []

        for chunk in doc_chunks:

            chunk_words = re.findall(
                r"\w+",
                chunk["content"].lower(),
            )

            chunk_word_set = set(chunk_words)

            overlap = query_words.intersection(
                chunk_word_set
            )

            if overlap:

                score = (
                    len(overlap)
                    / (
                        math.log(
                            len(chunk_words) + 1
                        )
                        + 1.0
                    )
                )

                scored.append(
                    (score, chunk)
                )

        # Highest score first
        scored.sort(
            key=lambda item: item[0],
            reverse=True,
        )

        return [
            item[1]
            for item in scored[:top_k]
        ]

    # =====================================================
    # MAIN TOOL
    # =====================================================

    def run(self, **kwargs) -> ToolResult:

        query = kwargs.get(
            "query",
            "",
        )

        try:
            top_k = int(
                kwargs.get(
                    "top_k",
                    3,
                )
            )
        except (TypeError, ValueError):
            top_k = 3

        if top_k <= 0:
            top_k = 3

        # =================================================
        # VALIDATE QUERY
        # =================================================

        if not query.strip():

            return ToolResult(
                success=False,
                output="",
                error="Search query is empty.",
            )

        try:

            # =================================================
            # MEMBER 3 RETRIEVER
            # =================================================

            if self.external_retriever:

                results = self.external_retriever(
                    query,
                    top_k,
                )

            # =================================================
            # LOCAL FALLBACK
            # =================================================

            else:

                results = self._fallback_local_search(
                    query,
                    top_k,
                )

            # =================================================
            # NO RESULTS
            # =================================================

            if not results:

                return ToolResult(
                    success=True,
                    output=(
                        "No matching documents found in "
                        f"knowledge base for query: '{query}'."
                    ),
                    data={
                        "query": query,
                        "results": [],
                    },
                )

            # =================================================
            # FORMAT RESULTS
            # =================================================

            formatted = [
                f"Found {len(results)} relevant knowledge chunks:"
            ]

            for index, result in enumerate(
                results,
                start=1,
            ):

                source = result.get(
                    "source",
                    "Enterprise Knowledge",
                )

                content = result.get(
                    "content",
                    "",
                ).strip()

                formatted.append(
                    f"\n--- [Source: {source}] "
                    f"(Result {index}) ---\n"
                    f"{content}"
                )

            final_output = "\n".join(
                formatted
            )

            # =================================================
            # RETURN SUCCESS
            # =================================================

            return ToolResult(
                success=True,
                output=final_output,
                data={
                    "query": query,
                    "results": results,
                },
            )

        except Exception as e:

            return ToolResult(
                success=False,
                output="",
                error=(
                    f"RAG search failed: {str(e)}"
                ),
            )