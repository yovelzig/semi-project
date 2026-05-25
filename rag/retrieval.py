import faiss

from rag.embeddings import embed_query_with_huggingface


TOP_K = 5
MIN_SCORE = 0.55


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

    for score, idx in zip(scores[0], indexes[0]):
        if idx == -1:
            continue

        if score < MIN_SCORE:
            continue

        results.append({
            "score": float(score),
            "text": chunks[idx]
        })

    return results