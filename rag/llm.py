import os
import sys

from google import genai
from google.genai import types

GEMINI_MODEL = "gemini-3-flash-preview"
# ==========================
# API Clients
# ==========================

def create_gemini_client():
    api_key = os.environ.get("GEMINI_API_KEY")
    
    if not api_key:
        print("ERROR: GEMINI_API_KEY is missing.")
        print('PowerShell: $env:GEMINI_API_KEY="your_gemini_api_key"')
        sys.exit(1)

    return genai.Client(api_key=api_key)

# ==========================
# Gemini LLM
# ==========================


def ask_gemini(context, question):
    """
    Gemini is the LLM.
    Hugging Face is only used for embeddings.
    """
    prompt = f"""
You are a helpful RAG assistant.

Use the provided context to answer the user's question.

Rules:
1. First answer using only the provided context.
2. If the context does not contain enough information, say:
   "I do not have enough information in the documents, but based on general knowledge..."
3. Keep the answer simple and clear.
4. Do not invent document facts.

Context:
{context}

Question:
{question}

Answer:
"""

    response = gemini_client.models.generate_content(
        model=GEMINI_MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=0.3,
            max_output_tokens=500,
            thinking_config=types.ThinkingConfig(
                thinking_budget=0
            )
        )
    )

    return response.text.strip()

gemini_client = create_gemini_client()