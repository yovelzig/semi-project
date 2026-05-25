import os
import sys
import time
import numpy as np
from nltk.tokenize import sent_tokenize
import nltk
from google import genai
from huggingface_hub import InferenceClient


def setup_nltk():
    nltk.download("punkt", quiet=True)
    nltk.download("punkt_tab", quiet=True)

DATA_FOLDER = "data"
# Hugging Face embedding model running in the cloud
HF_EMBEDDING_MODEL = "ibm-granite/granite-embedding-97m-multilingual-r2"

# We use a small batch size to avoid hitting rate limits on the Hugging Face API.
BATCH_SIZE = 8

# ==========================
# API Clients
# ==========================

def create_huggingface_client():
    hf_token = os.environ.get("HF_TOKEN")

    if not hf_token:
        print("ERROR: HF_TOKEN is missing.")
        print('PowerShell: $env:HF_TOKEN="your_huggingface_token"')
        sys.exit(1)

    return InferenceClient(
        provider="hf-inference",
        api_key=hf_token
    )



hf_client = create_huggingface_client()
# ==========================
# Load Documents
# ==========================

def load_documents(folder=DATA_FOLDER):
    """
    Loads .txt files and splits them into sentences.
    We keep the original sentence text.
    Do NOT remove stopwords here, because the LLM needs natural context.
    """
    if not os.path.exists(folder):
        raise FileNotFoundError(
            f"Folder '{folder}' does not exist. Create it and put .txt files inside."
        )

    chunks = []

    for file_name in os.listdir(folder):
        if file_name.endswith(".txt"):
            file_path = os.path.join(folder, file_name)

            with open(file_path, "r", encoding="utf-8") as file:
                text = file.read()

            sentences = sent_tokenize(text)

            for sentence in sentences:
                sentence = sentence.strip()
                if sentence:
                    chunks.append(sentence)

    if not chunks:
        raise ValueError(
            f"No text found. Make sure '{folder}' contains .txt files with content."
        )

    print(f"Loaded {len(chunks)} text chunks.")
    return chunks



# ==========================
# Hugging Face Cloud Embeddings
# ==========================

def normalize_hf_embedding_output(output):
    """
    Hugging Face feature_extraction can return different shapes depending
    on the model/provider.

    We convert it into a clean 2D numpy array:
    shape = [number_of_texts, embedding_dimension]
    """
    arr = np.array(output, dtype="float32")

    # Case 1:
    # Single text embedding:
    # [dimension]
    if arr.ndim == 1:
        arr = np.expand_dims(arr, axis=0)

    # Case 2:
    # Token embeddings:
    # [tokens, dimension]
    # We mean-pool tokens into one sentence vector.
    elif arr.ndim == 2:
        # If this is already [batch, dim], keep it.
        # If this came from one text as [tokens, dim], this is ambiguous.
        # For a single input call, we treat it as token embeddings.
        pass

    # Case 3:
    # Batch token embeddings:
    # [batch, tokens, dimension]
    elif arr.ndim == 3:
        arr = arr.mean(axis=1)

    return arr.astype("float32")


def embed_texts_with_huggingface(texts, batch_size=BATCH_SIZE):
    """
    Creates embeddings using Hugging Face cloud inference.
    """
    all_embeddings = []

    for start in range(0, len(texts), batch_size):
        batch = texts[start:start + batch_size]

        print(f"Embedding batch {start // batch_size + 1}...")
        # מכאן מתבצעת קריאה ל-Hugging Face עבור כל אצווה של טקסטים, והתוצאה מנורמלת לפורמט אחיד של מערך דו-ממדי שבו כל שורה היא וקטור ההטבעה של טקסט אחד.
        result = hf_client.feature_extraction(
            batch,
            model=HF_EMBEDDING_MODEL
        )

        embeddings = normalize_hf_embedding_output(result)

        # Safety check:
        # Sometimes a provider may return token-level embeddings for each item.
        # If the batch returns 3D, it was already mean-pooled above.
        if embeddings.shape[0] != len(batch):
            fixed_embeddings = []

            for text in batch:
                single_result = hf_client.feature_extraction(
                    text,
                    model=HF_EMBEDDING_MODEL
                )

                single_embedding = np.array(single_result, dtype="float32")

                if single_embedding.ndim == 1:
                    pass
                elif single_embedding.ndim == 2:
                    single_embedding = single_embedding.mean(axis=0)
                elif single_embedding.ndim == 3:
                    single_embedding = single_embedding.mean(axis=1)[0]

                fixed_embeddings.append(single_embedding)

                time.sleep(0.1)

            embeddings = np.array(fixed_embeddings, dtype="float32")

        all_embeddings.append(embeddings)

    final_embeddings = np.vstack(all_embeddings).astype("float32")

    print(f"Created embeddings shape: {final_embeddings.shape}")

    return final_embeddings

# This function is used for embedding the user query at retrieval time, ensuring it goes through the same Hugging Face embedding process as the documents.
def embed_query_with_huggingface(query):
    """
    Creates one query embedding using Hugging Face cloud inference.
    """
    result = hf_client.feature_extraction(
        query,
        model=HF_EMBEDDING_MODEL
    )

    embedding = np.array(result, dtype="float32")

    if embedding.ndim == 1:
        embedding = np.expand_dims(embedding, axis=0)

    elif embedding.ndim == 2:
        # Token embeddings -> mean pooling
        embedding = embedding.mean(axis=0, keepdims=True)

    elif embedding.ndim == 3:
        embedding = embedding.mean(axis=1)

    return embedding.astype("float32")

