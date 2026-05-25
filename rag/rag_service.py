from rag.ingestion import load_documents
from rag.embeddings import embed_texts_with_huggingface
from rag.vector_store import create_faiss_index
from rag.retrieval import retrieve
from rag.llm import ask_gemini


class RagService:
    """
    Handles the full RAG flow.
    """

    def __init__(self):
        self.chunks = []
        self.embeddings = None
        self.index = None

        self.rebuild_index()

    def rebuild_index(self):
        """
        Reloads all documents and rebuilds the FAISS index.
        Use this after uploading new files.
        """

        print("Rebuilding RAG index...")

        self.chunks = load_documents()
        self.embeddings = embed_texts_with_huggingface(self.chunks)
        self.index = create_faiss_index(self.embeddings)

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