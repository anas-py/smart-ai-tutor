"""
AI Tutor — RAG Engine
ChromaDB + PDF ingestion + semantic retrieval
"""

import os
import re
import uuid
import hashlib
from typing import List, Optional

try:
    import fitz  # PyMuPDF
    PYMUPDF_OK = True
except ImportError:
    PYMUPDF_OK = False

try:
    import PyPDF2
    PYPDF2_OK = True
except ImportError:
    PYPDF2_OK = False

try:
    import chromadb
    from chromadb.utils import embedding_functions
    CHROMA_OK = True
except ImportError:
    CHROMA_OK = False


def _extract_text_from_pdf(path: str) -> str:
    """Extract text from PDF using PyMuPDF (preferred) or PyPDF2 fallback."""
    text = ""

    if PYMUPDF_OK:
        try:
            doc = fitz.open(path)
            for page in doc:
                text += page.get_text() + "\n"
            doc.close()
            return text.strip()
        except Exception as e:
            print(f"PyMuPDF failed: {e}")

    if PYPDF2_OK:
        try:
            with open(path, "rb") as f:
                reader = PyPDF2.PdfReader(f)
                for page in reader.pages:
                    text += (page.extract_text() or "") + "\n"
            return text.strip()
        except Exception as e:
            print(f"PyPDF2 failed: {e}")

    return ""


def _chunk_text(text: str, chunk_size: int = 600, overlap: int = 100) -> List[str]:
    """Split text into overlapping chunks for better retrieval."""
    # Clean up whitespace
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = re.sub(r' {2,}', ' ', text)

    sentences = re.split(r'(?<=[.!?])\s+', text)
    chunks = []
    current = ""

    for sentence in sentences:
        if len(current) + len(sentence) <= chunk_size:
            current += " " + sentence
        else:
            if current.strip():
                chunks.append(current.strip())
            # Overlap: keep last part of previous chunk
            words = current.split()
            overlap_text = " ".join(words[-overlap // 6:]) if len(words) > overlap // 6 else ""
            current = overlap_text + " " + sentence

    if current.strip():
        chunks.append(current.strip())

    return [c for c in chunks if len(c) > 50]


class RAGEngine:
    """
    Per-user ChromaDB RAG engine.
    Each user gets their own isolated collection.
    """

    def __init__(self, persist_dir: str = None):
        self.persist_dir = persist_dir or os.path.join(
            os.path.dirname(__file__), "..", "..", "instance", "chroma_db"
        )
        os.makedirs(self.persist_dir, exist_ok=True)
        self.client = None
        self._init()

    def _init(self):
        if not CHROMA_OK:
            print("⚠️  ChromaDB not installed. RAG disabled.")
            return
        try:
            self.client = chromadb.PersistentClient(path=self.persist_dir)
            print(f"✅ RAGEngine: ChromaDB ready at {self.persist_dir}")
        except Exception as e:
            print(f"⚠️  ChromaDB init failed: {e}")
            self.client = None

    def _collection_name(self, user_id: int) -> str:
        return f"user_{user_id}_docs"

    def _get_collection(self, user_id: int):
        if not self.client:
            return None
        try:
            ef = embedding_functions.DefaultEmbeddingFunction()
            return self.client.get_or_create_collection(
                name=self._collection_name(user_id),
                embedding_function=ef,
                metadata={"hnsw:space": "cosine"}
            )
        except Exception as e:
            print(f"Collection error: {e}")
            return None

    def ingest_pdf(self, user_id: int, pdf_path: str, filename: str) -> dict:
        """
        Extract text from PDF, chunk it, embed and store in ChromaDB.
        Returns status dict.
        """
        if not self.client:
            return {"success": False, "error": "ChromaDB not available", "chunks": 0}

        # Extract text
        text = _extract_text_from_pdf(pdf_path)
        if not text:
            return {"success": False, "error": "Could not extract text from PDF. Make sure it's not a scanned image-only PDF.", "chunks": 0}

        if len(text) < 100:
            return {"success": False, "error": "PDF has very little readable text.", "chunks": 0}

        # Chunk
        chunks = _chunk_text(text)
        if not chunks:
            return {"success": False, "error": "No content chunks generated.", "chunks": 0}

        # Get collection
        collection = self._get_collection(user_id)
        if not collection:
            return {"success": False, "error": "Could not create knowledge base.", "chunks": 0}

        # Create a doc_id based on filename hash for deduplication
        doc_id = hashlib.md5(filename.encode()).hexdigest()[:12]

        # Remove existing chunks from this file if re-uploading
        try:
            existing = collection.get(where={"doc_id": doc_id})
            if existing["ids"]:
                collection.delete(ids=existing["ids"])
        except Exception:
            pass

        # Store chunks
        ids = [f"{doc_id}_{i}" for i in range(len(chunks))]
        metadatas = [{"doc_id": doc_id, "filename": filename, "chunk_index": i} for i in range(len(chunks))]

        try:
            collection.add(documents=chunks, ids=ids, metadatas=metadatas)
            return {
                "success": True,
                "chunks": len(chunks),
                "filename": filename,
                "doc_id": doc_id,
                "preview": text[:300] + "..." if len(text) > 300 else text
            }
        except Exception as e:
            return {"success": False, "error": str(e), "chunks": 0}

    def retrieve(self, user_id: int, query: str, n_results: int = 4) -> List[str]:
        """
        Retrieve top-N relevant chunks for a query from user's collection.
        Returns list of text chunks.
        """
        if not self.client:
            return []

        collection = self._get_collection(user_id)
        if not collection:
            return []

        try:
            count = collection.count()
            if count == 0:
                return []

            n_results = min(n_results, count)
            results = collection.query(
                query_texts=[query],
                n_results=n_results
            )
            return results["documents"][0] if results["documents"] else []
        except Exception as e:
            print(f"RAG retrieve error: {e}")
            return []

    def list_documents(self, user_id: int) -> List[dict]:
        """List all documents uploaded by a user."""
        if not self.client:
            return []

        collection = self._get_collection(user_id)
        if not collection:
            return []

        try:
            if collection.count() == 0:
                return []
            all_items = collection.get(include=["metadatas"])
            seen = {}
            for meta in all_items["metadatas"]:
                doc_id = meta.get("doc_id", "")
                if doc_id not in seen:
                    seen[doc_id] = {"doc_id": doc_id, "filename": meta.get("filename", "Unknown")}
            return list(seen.values())
        except Exception as e:
            print(f"List docs error: {e}")
            return []

    def delete_document(self, user_id: int, doc_id: str) -> bool:
        """Delete all chunks from a specific document."""
        if not self.client:
            return False

        collection = self._get_collection(user_id)
        if not collection:
            return False

        try:
            existing = collection.get(where={"doc_id": doc_id})
            if existing["ids"]:
                collection.delete(ids=existing["ids"])
            return True
        except Exception as e:
            print(f"Delete doc error: {e}")
            return False

    def clear_user_docs(self, user_id: int) -> bool:
        """Clear all documents for a user."""
        if not self.client:
            return False
        try:
            self.client.delete_collection(self._collection_name(user_id))
            return True
        except Exception as e:
            print(f"Clear docs error: {e}")
            return False


# Singleton instance
_rag_engine: Optional[RAGEngine] = None


def get_rag_engine() -> RAGEngine:
    global _rag_engine
    if _rag_engine is None:
        _rag_engine = RAGEngine()
    return _rag_engine
