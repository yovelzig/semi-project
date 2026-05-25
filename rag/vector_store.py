import faiss
# ==========================
# FAISS
# ==========================

# This function creates a FAISS index from the Hugging Face embeddings. It uses a simple IndexFlatL2 for demonstration, which is an exact search index. For larger datasets, you might want to use an approximate index like IndexIVFFlat or IndexHNSW.
def create_faiss_index(embeddings):
    """
    Creates FAISS index from Hugging Face embeddings.
    """
    dimension = embeddings.shape[1]

    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings)

    print(f"FAISS index created with {index.ntotal} vectors.")
    return index
