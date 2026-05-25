from dotenv import load_dotenv
load_dotenv()

from rag.ingestion import load_documents
from rag.embeddings import embed_texts_with_huggingface
from rag.vector_store import create_faiss_index
from rag.retrieval import retrieve
from rag.llm import ask_gemini



def main():
    print("Starting RAG test...")

    # 1. Load text files from data folder
    chunks = load_documents()

    print("\nFirst chunks loaded:")
    for i, chunk in enumerate(chunks[:5], start=1):
        print(f"{i}. {chunk}")

    # 2. Convert chunks to embeddings
    embeddings = embed_texts_with_huggingface(chunks)

    # 3. Create FAISS index
    index = create_faiss_index(embeddings)

    # 4. Ask a test question
    question = "What is DNS?"

    print("\nQuestion:")
    print(question)

    # 5. Retrieve relevant chunks
    retrieved_chunks = retrieve(question, index, chunks)

    print("\nRetrieved chunks:")
    for i, chunk in enumerate(retrieved_chunks, start=1):
        print(f"{i}. {chunk}")

    # 6. Build context
    context = "\n".join(retrieved_chunks)

    # 7. Ask Gemini
    answer = ask_gemini(context, question)

    print("\nFinal answer:")
    print(answer)


if __name__ == "__main__":
    main()