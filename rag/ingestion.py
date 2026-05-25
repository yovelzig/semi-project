import os

import nltk
from nltk.tokenize import sent_tokenize


DATA_FOLDER = "data"


def setup_nltk():
    """
    Downloads the required NLTK tokenizer data.
    """
    nltk.download("punkt", quiet=True)
    nltk.download("punkt_tab", quiet=True)


def load_documents(folder=DATA_FOLDER):
    """
    Loads .txt files from the data folder and splits them into sentence chunks.
    """

    setup_nltk()

    if not os.path.exists(folder):
        raise FileNotFoundError(
            f"Folder '{folder}' does not exist. Create it and put .txt files inside."
        )

    chunks = []

    for file_name in os.listdir(folder):
        if not file_name.endswith(".txt"):
            continue

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