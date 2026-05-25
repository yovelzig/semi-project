import os


DATA_FOLDER = "data"


def split_text_into_chunks(text):
    """
    Splits text into meaningful chunks.

    The current project data is mostly FAQ / troubleshooting text.
    Therefore, paragraph-based chunks are better than sentence-based chunks,
    because a question and its answer should stay together.
    """

    raw_chunks = text.split("\n\n")

    chunks = []

    for chunk in raw_chunks:
        cleaned_chunk = chunk.strip()

        if cleaned_chunk:
            chunks.append(cleaned_chunk)

    return chunks


def load_documents(folder=DATA_FOLDER):
    """
    Loads .txt files from the data folder and splits them into paragraph chunks.
    """

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

        file_chunks = split_text_into_chunks(text)

        for chunk in file_chunks:
            chunks.append(f"Source file: {file_name}\n\n{chunk}")

    if not chunks:
        raise ValueError(
            f"No text found. Make sure '{folder}' contains .txt files with content."
        )

    print(f"Loaded {len(chunks)} text chunks.")

    return chunks