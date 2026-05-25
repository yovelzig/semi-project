import os

from dotenv import load_dotenv

load_dotenv()

from flask import Flask, request, jsonify, render_template
from werkzeug.utils import secure_filename

from rag.rag_service import RagService

app = Flask(__name__)

UPLOAD_FOLDER = "data"

ALLOWED_EXTENSIONS = {
    "txt",
    "md",
    "csv",
    "json",
    "pdf",
    "docx",
    "xlsx",
}

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

def allowed_file(filename):
    """
    Checks if the uploaded file extension is supported.
    """

    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS
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

@app.route("/upload", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        return jsonify({
            "error": "No file was uploaded."
        }), 400

    file = request.files["file"]

    if file.filename == "":
        return jsonify({
            "error": "No file selected."
        }), 400

    if not allowed_file(file.filename):
        return jsonify({
            "error": "Unsupported file type."
        }), 400

    filename = secure_filename(file.filename)
    save_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)

    file.save(save_path)

    rag_service.rebuild_index()

    return jsonify({
        "message": "File uploaded successfully and RAG index rebuilt.",
        "filename": filename
    })

@app.route("/files", methods=["GET"])
def list_files():
    files = []

    for filename in os.listdir(app.config["UPLOAD_FOLDER"]):
        file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)

        if os.path.isfile(file_path) and allowed_file(filename):
            files.append(filename)

    return jsonify({
        "files": files
    })

if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)