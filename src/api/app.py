from flask import Flask, jsonify

app = Flask(__name__)


@app.route("/")
def index():
    return "ValoRe service is running. API routes will be extended in the next step."


@app.route("/health")
def health():
    return jsonify({"status": "healthy"})
