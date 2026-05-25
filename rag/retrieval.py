import faiss

from rag.embeddings import embed_query_with_huggingface


TOP_K = 3


def retrieve(query, index, chunks, k=TOP_K):
    """
    Converts query to Hugging Face embedding, normalizes it,
    then searches FAISS for the most relevant chunks.
    """

    query_embedding = embed_query_with_huggingface(query)

    faiss.normalize_L2(query_embedding)

    scores, indexes = index.search(query_embedding, k)

    print("\nFAISS scores:", scores)
    print("FAISS indexes:", indexes)

    results = []

    for idx in indexes[0]:
        if idx != -1:
            results.append(chunks[idx])

    return results