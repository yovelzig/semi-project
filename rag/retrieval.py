
from embedding import embed_query_with_huggingface

TOP_K = 3

def retrieve(query, index, chunks, k=TOP_K):
    """
    Converts query to Hugging Face embedding, then searches FAISS.
    """
    query_embedding = embed_query_with_huggingface(query)

    distances, indexes = index.search(query_embedding, k)

    print("\nFAISS distances:", distances)
    print("FAISS indexes:", indexes)

    results = []

    for idx in indexes[0]:
        if idx != -1:
            results.append(chunks[idx])

    return results

