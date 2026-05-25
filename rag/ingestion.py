import json
import os

import pandas as pd
from docx import Document
from pypdf import PdfReader


DATA_FOLDER = "data"


SUPPORTED_EXTENSIONS = {
    ".txt",
    ".md",
    ".csv",
    ".json",
    ".pdf",
    ".docx",
    ".xlsx",
}

def split_text_into_chunks(text):
    """
    Splits text into paragraph-based chunks.
    This keeps related lines together and works better for FAQ-style documents.
    """

    raw_chunks = text.split("\n\n")

    chunks = []

    for chunk in raw_chunks:
        cleaned_chunk = chunk.strip()

        if cleaned_chunk:
            chunks.append(cleaned_chunk)

    return chunks


def load_text_file(file_path):
    """
    Loads plain text based files.
    Supports .txt and .md.
    """

    with open(file_path, "r", encoding="utf-8") as file:
        return file.read()


def load_csv_file(file_path):
    """
    Loads a CSV file and converts it into readable text for RAG.
    """

    df = pd.read_csv(file_path)

    lines = []

    lines.append(f"CSV file with {len(df)} rows and {len(df.columns)} columns.")
    lines.append(f"Columns: {', '.join(df.columns)}")
    lines.append("")
    lines.append("Data preview:")
    lines.append(df.head(20).to_string(index=False))

    return "\n".join(lines)

def load_pdf_file(file_path):
    """
    Loads a PDF file and extracts text from all pages.
    """

    reader = PdfReader(file_path)
    pages_text = []

    for page_number, page in enumerate(reader.pages, start=1):
        text = page.extract_text()

        if text:
            pages_text.append(
                f"Page {page_number}:\n{text.strip()}"
            )

    if not pages_text:
        return "No readable text was found in this PDF."

    return "\n\n".join(pages_text)


def load_docx_file(file_path):
    """
    Loads a Word DOCX file and extracts text from paragraphs.
    """

    document = Document(file_path)

    paragraphs = []

    for paragraph in document.paragraphs:
        text = paragraph.text.strip()

        if text:
            paragraphs.append(text)

    if not paragraphs:
        return "No readable text was found in this DOCX file."

    return "\n\n".join(paragraphs)


def load_xlsx_file(file_path):
    """
    Loads an Excel XLSX file and converts all sheets into readable text.
    """

    excel_file = pd.ExcelFile(file_path)

    sheet_texts = []

    for sheet_name in excel_file.sheet_names:
        df = pd.read_excel(file_path, sheet_name=sheet_name)

        lines = [
            f"Excel sheet: {sheet_name}",
            f"Rows: {len(df)}",
            f"Columns: {', '.join(str(col) for col in df.columns)}",
            "",
            "Data preview:",
            df.head(20).to_string(index=False),
        ]

        sheet_texts.append("\n".join(lines))

    return "\n\n".join(sheet_texts)

def load_json_file(file_path):
    """
    Loads a JSON file and converts it into readable text for RAG.
    """

    with open(file_path, "r", encoding="utf-8") as file:
        data = json.load(file)

    return json.dumps(data, indent=2, ensure_ascii=False)


def extract_text_from_file(file_path):
    """
    Detects file type by extension and extracts readable text.
    """

    _, extension = os.path.splitext(file_path)
    extension = extension.lower()

    if extension in [".txt", ".md"]:
        return load_text_file(file_path)

    if extension == ".csv":
        return load_csv_file(file_path)

    if extension == ".json":
        return load_json_file(file_path)

    if extension == ".pdf":
        return load_pdf_file(file_path)

    if extension == ".docx":
        return load_docx_file(file_path)

    if extension == ".xlsx":
        return load_xlsx_file(file_path)

    raise ValueError(f"Unsupported file type: {extension}")

def load_documents(folder=DATA_FOLDER):
    """
    Loads supported files from the data folder and converts them into chunks.
    """

    if not os.path.exists(folder):
        raise FileNotFoundError(
            f"Folder '{folder}' does not exist. Create it and put supported files inside."
        )

    chunks = []

    for file_name in os.listdir(folder):
        file_path = os.path.join(folder, file_name)

        if not os.path.isfile(file_path):
            continue

        _, extension = os.path.splitext(file_name)
        extension = extension.lower()

        if extension not in SUPPORTED_EXTENSIONS:
            print(f"Skipping unsupported file: {file_name}")
            continue

        print(f"Loading file: {file_name}")

        text = extract_text_from_file(file_path)

        file_chunks = split_text_into_chunks(text)

        for chunk in file_chunks:
            chunks.append(
                f"Source file: {file_name}\n\n{chunk}"
            )

    if not chunks:
        raise ValueError(
            f"No supported content found. Supported extensions: {SUPPORTED_EXTENSIONS}"
        )

    print(f"Loaded {len(chunks)} text chunks.")

    return chunks