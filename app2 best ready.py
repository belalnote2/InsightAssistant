"""
Flask-based micro-service that:
1. Receives free-text articles.
2. Sends the text to a local Ollama (Llama 3) instance for analysis
   (summary, people, category).
3. save both the raw text and the AI-generated metadata in a SQLite DB.

"""

import os
#import logging
import json
from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import requests

# ── Logging setup ────────────────────────────────────────────────────────────
#logging.basicConfig(level=logging.INFO)              # Global log level
#logger = logging.getLogger(__name__)                 # Module-level logger

# ── Path & DB initialisation ────────────────────────────────────────────────
#   Create a ./db/ folder (ignored if it already exists)
os.makedirs("db", exist_ok=True)

#   Absolute path to this file’s directory
basedir = os.path.abspath(os.path.dirname(__file__))

#   SQLite database file …/db/insight.db
db_path = os.path.join(basedir, "db", "insight.db")
db_uri  = "sqlite:///" + db_path.replace("\\", "/")  # Windows-safe slashes

# ── Flask & SQLAlchemy setup ────────────────────────────────────────────────
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"]        = db_uri
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False  # Performance tweak

db = SQLAlchemy(app)

# ── DB model ────────────────────────────────────────────────────────────────
class Analysis(db.Model):
    """ORM mapping for one analysed article."""
    id            = db.Column(db.Integer, primary_key=True)
    original_text = db.Column(db.Text,   nullable=False)
    summary       = db.Column(db.Text)
    persons       = db.Column(db.Text)           # Comma-separated list
    category      = db.Column(db.String(120))    # e.g. “Technology”

# Create tables on start-up (only if they don’t exist yet)
with app.app_context():
    db.create_all()

# ── Helper: talk to local Ollama instance ───────────────────────────────────
def call_ollama(text: str) -> dict:
    """
    Send *text* to the Ollama HTTP API and return a dict:
        { "summary": str, "persons": [str], "category": str }
    On any error, return a fallback response.
    """
    prompt = f"""Analyze the following article and provide:
    1. A concise summary (2-3 sentences)
    2. All person names mentioned (comma-separated)
    3. The most relevant category \
(News, Technology, Sports, Politics, Business, Science, Entertainment, Health, Other)

    Return your response as a valid JSON object with these keys: \
"summary", "persons", "category"

    Article:
    {text}

    Response:"""

    payload = {
        "model":  "mistral",  # Changed from llama3 to mistral (the model installed on this PC)
        "prompt": prompt,
        "format": "json",
        "stream": False
    }

    try:
        resp = requests.post("http://localhost:11434/api/generate", json=payload, timeout=120)
        resp.raise_for_status()
        data = resp.json()

        # Check if "response" exists and try parsing it
        if "response" in data:
            try:
                parsed = json.loads(data["response"])
                return {
                    "summary":  parsed.get("summary", ""),
                    "persons":  parsed.get("persons", []),
                    "category": parsed.get("category", "Other")
                }
            except Exception:
                print("Problem parsing JSON from Ollama.")
        else:
            print("No 'response' in Ollama reply.")

    except Exception:
        print("Failed to call Ollama.")

    # Fallback if anything went wrong
    return fallback_response(text)

def fallback_response(text: str) -> dict:
    """
    Custom minimal result if Ollama is unavailable.
    """
    return {
        "original_text": text,
        "summary": "No summary, error",
        "persons": "No people, error",
        "category": "Other"
    }


# ── Routes ──────────────────────────────────────────────────────────────────
@app.route("/")
def index():
    """Display the 10 most-recent analyses in a simple HTML table."""
    entries = Analysis.query.order_by(Analysis.id.desc()).limit(10).all()
    return render_template("index.html", entries=entries)

@app.route("/analyze", methods=["POST"])
def analyze():
    """
    Accept text   forward to Ollama →
    save result  return JSON payload:
        { summary, persons, category, id }
    """
    # Extract the text from the incoming request, no matter the format
    text = request.form.get("text", "").strip()

    try:
        ai_res = call_ollama(text)

        # Ensure persons are a single string for DB storage
        persons_str = ", ".join(ai_res["persons"]) \
            if isinstance(ai_res["persons"], list) \
            else ai_res["persons"]

        # save result
        new_entry = Analysis(
            original_text=text,
            summary=ai_res["summary"],
            persons=persons_str,
            category=ai_res["category"]
        )
        db.session.add(new_entry)
        db.session.commit()

        # Echo JSON back to the caller (e.g. your JS front-end)
        return jsonify({
            "summary":  ai_res["summary"],
            "persons":  persons_str,
            "category": ai_res["category"],
            "id":       new_entry.id
        })

    except Exception as exc:

        db.session.rollback()
        return jsonify({"error": "Analysis failed"}), 500

# ── NEW FEATURE: Export to JSON ─────────────────────────────────────────────
# This route allows users to download all analyses as a JSON file
# Added by: Student Project
@app.route("/export")
def export_to_json():
    """
    Export all saved analyses to a JSON file.
    Returns: JSON file with summary, category, and persons for each analysis
    """
    # Get all analyses from the database
    all_entries = Analysis.query.all()

    # Create a list to hold all the data
    export_data = []

    # Loop through each analysis and add it to our list
    for entry in all_entries:
        export_data.append({
            "id": entry.id,
            "summary": entry.summary,
            "category": entry.category,
            "persons": entry.persons,
            "original_text": entry.original_text
        })

    # Return the data as JSON with proper formatting
    # The jsonify function converts our Python list to JSON format
    return jsonify(export_data)

# ── Main entry point ────────────────────────────────────────────────────────
if __name__ == "__main__":
    # Accessible from  host machine at http://localhost:5000/
    
    app.run(host="0.0.0.0", port=5000, debug=True)
