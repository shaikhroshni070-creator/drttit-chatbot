"""DR TTIT College Chatbot - free Flask version (no AI service, no API key).

Answers come from the built-in replies in college_data.json. Questions about
fees always get the fixed reply with the admission and office numbers.
"""
import json
import os
import re
from pathlib import Path

from flask import Flask, jsonify, render_template, request

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:  # python-dotenv is optional
    pass

BASE_DIR = Path(__file__).resolve().parent

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "change-me")
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024

with open(BASE_DIR / "college_data.json", encoding="utf-8") as f:
    DATA = json.load(f)

FEE_WORDS = set(DATA["fee_words"])


def tokenize(text: str) -> set:
    return set(re.findall(r"[a-z0-9]+", text.lower()))


def get_reply(message: str) -> str:
    tokens = tokenize(message)

    # Any fee-related question gets the same fixed reply.
    if tokens & FEE_WORDS:
        return DATA["fees_reply"]

    best_score, best_reply = 0, None
    for intent in DATA["intents"]:  # earlier intents win ties
        score = sum(1 for keyword in intent["keywords"] if keyword in tokens)
        if score > best_score:
            best_score, best_reply = score, intent["response"]

    return best_reply or DATA["fallback"]


@app.route("/")
def home():
    return render_template(
        "index.html",
        college=DATA["college"],
        suggestions=DATA["suggestions"],
    )


@app.route("/chat", methods=["POST"])
def chat():
    payload = request.get_json(silent=True) or {}
    message = (payload.get("message") or "").strip()

    if not message:
        return jsonify({"reply": "Please enter your question."}), 400

    if len(message) > 1000:
        return jsonify({
            "reply": "Please keep your question below 1000 characters."
        }), 400

    return jsonify({"reply": get_reply(message)})


@app.errorhandler(413)
def too_large(error):
    return jsonify({"reply": "Your request is too large."}), 413


if __name__ == "__main__":
    app.run(
        debug=os.getenv("FLASK_DEBUG", "0") == "1",
        port=int(os.getenv("PORT", "5000")),
    )
