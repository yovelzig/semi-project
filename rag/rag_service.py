import json
import os

import faiss

from rag.ingestion import DATA_FOLDER, SUPPORTED_EXTENSIONS, load_documents
from rag.embeddings import embed_texts_with_huggingface
from rag.vector_store import create_faiss_index
from rag.retrieval import retrieve
from rag.llm import ask_gemini


CACHE_FOLDER = "database/rag_cache"
INDEX_PATH = os.path.join(CACHE_FOLDER, "faiss.index")
CHUNKS_PATH = os.path.join(CACHE_FOLDER, "chunks.json")
META_PATH = os.path.join(CACHE_FOLDER, "metadata.json")


class RagService:
    """
    Handles the full RAG flow.
    Uses cache so the FAISS index is not rebuilt on every app startup.
    """

    def __init__(self):
        self.chunks = []
        self.index = None

        self.load_or_rebuild_index()

    def get_data_fingerprint(self):
        """
        Creates a simple fingerprint from file names, sizes and modified times.
        If any supported file changes, the fingerprint changes.
        """

        fingerprint_items = []

        if not os.path.exists(DATA_FOLDER):
            return fingerprint_items

        for file_name in sorted(os.listdir(DATA_FOLDER)):
            file_path = os.path.join(DATA_FOLDER, file_name)

            if not os.path.isfile(file_path):
                continue

            _, extension = os.path.splitext(file_name)
            extension = extension.lower()

            if extension not in SUPPORTED_EXTENSIONS:
                continue

            stat = os.stat(file_path)

            fingerprint_items.append({
                "file_name": file_name,
                "size": stat.st_size,
                "modified_time": stat.st_mtime_ns,
            })

        return fingerprint_items

    def cache_exists(self):
        return (
            os.path.exists(INDEX_PATH)
            and os.path.exists(CHUNKS_PATH)
            and os.path.exists(META_PATH)
        )

    def load_cache_metadata(self):
        with open(META_PATH, "r", encoding="utf-8") as file:
            return json.load(file)

    def is_cache_valid(self):
        if not self.cache_exists():
            return False

        current_fingerprint = self.get_data_fingerprint()
        cached_metadata = self.load_cache_metadata()

        return cached_metadata.get("fingerprint") == current_fingerprint

    def load_cached_index(self):
        """
        Loads FAISS index and chunks from disk.
        """

        print("Loading RAG index from cache...")

        self.index = faiss.read_index(INDEX_PATH)

        with open(CHUNKS_PATH, "r", encoding="utf-8") as file:
            self.chunks = json.load(file)

        print(f"Loaded cached RAG index with {len(self.chunks)} chunks.")

    def save_cache(self):
        """
        Saves FAISS index, chunks and metadata to disk.
        """

        os.makedirs(CACHE_FOLDER, exist_ok=True)

        faiss.write_index(self.index, INDEX_PATH)

        with open(CHUNKS_PATH, "w", encoding="utf-8") as file:
            json.dump(self.chunks, file, ensure_ascii=False, indent=2)

        metadata = {
            "fingerprint": self.get_data_fingerprint()
        }

        with open(META_PATH, "w", encoding="utf-8") as file:
            json.dump(metadata, file, ensure_ascii=False, indent=2)

        print("RAG cache saved.")

    def load_or_rebuild_index(self):
        """
        Loads index from cache if possible.
        Otherwise rebuilds it.
        """

        if self.is_cache_valid():
            self.load_cached_index()
            return

        self.rebuild_index()

    def rebuild_index(self):
        """
        Reloads all documents and rebuilds the FAISS index.
        Use this after uploading new files.
        """

        print("Rebuilding RAG index...")

        self.chunks = load_documents()
        embeddings = embed_texts_with_huggingface(self.chunks)
        self.index = create_faiss_index(embeddings)

        self.save_cache()

        print("RAG index is ready.")

    def ask(self, question):
        """
        Receives a user question and returns an AI answer based on the documents.
        """

        retrieved_results = retrieve(question, self.index, self.chunks)

        retrieved_chunks = [item["text"] for item in retrieved_results]

        if not retrieved_chunks:
            return {
                "question": question,
                "answer": "I do not have enough information in the documents to answer this question.",
                "context": [],
                "sources": []
            }

        context = "\n\n---\n\n".join(retrieved_chunks)

        answer = ask_gemini(context, question)

        return {
            "question": question,
            "answer": answer,
            "context": retrieved_chunks,
            "sources": retrieved_results
        }