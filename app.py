from flask import Flask, jsonify, render_template, request
from rag_search import search_plants, generate_answer
from env import FLASK_DEBUG_MODE

app = Flask(__name__)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/search", methods=["POST"])
def search():
    data = request.get_json()

    prompt = data.get("question", "").strip()

    if not prompt:
        return jsonify({
            "error": "Please provide a question."
        }), 400

    # Retrieve relevant plants
    plants = search_plants(prompt, k=10)

    # Generate RAG answer
    answer = generate_answer(prompt, plants)

    return jsonify({
        "answer": answer,
        "plants": [
            {
                "common_name": plant["common_name"],
                "description": plant["description"]
            }
            for plant in plants
        ]
    })


if __name__ == "__main__":
    app.run(debug=FLASK_DEBUG_MODE)
