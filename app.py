from dotenv import load_dotenv

load_dotenv()

from flask import Flask, request, jsonify, render_template
from rag.rag_service import RagService


app = Flask(__name__)

# Initialize RAG service once when the app starts
rag_service = RagService()


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/ask", methods=["POST"])
def ask():
    data = request.get_json()

    if not data:
        return jsonify({
            "error": "Request body must be JSON."
        }), 400

    question = data.get("question")

    if not question or not question.strip():
        return jsonify({
            "error": "Question is required."
        }), 400

    result = rag_service.ask(question.strip())

    return jsonify(result)


if __name__ == "__main__":
    app.run(debug=True)