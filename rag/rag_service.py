from rag.ingestion import load_documents
from rag.embeddings import embed_texts_with_huggingface
from rag.vector_store import create_faiss_index
from rag.retrieval import retrieve
from rag.llm import ask_gemini


class RagService:
    """
    Handles the full RAG flow:
    1. Load documents
    2. Create embeddings
    3. Build FAISS index
    4. Retrieve relevant chunks
    5. Ask Gemini using retrieved context
    """

    def __init__(self):
        print("Initializing RAG service...")

        self.chunks = load_documents()
        self.embeddings = embed_texts_with_huggingface(self.chunks)
        self.index = create_faiss_index(self.embeddings)

        print("RAG service is ready.")

    def ask(self, question):
        """
        Receives a user question and returns an AI answer based on the documents.
        """

        retrieved_chunks = retrieve(question, self.index, self.chunks)

        context = "\n".join(retrieved_chunks)

        answer = ask_gemini(context, question)

        return {
            "question": question,
            "answer": answer,
            "context": retrieved_chunks
        }