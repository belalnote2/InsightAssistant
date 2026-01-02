# InsightAssistant

A Flask-based web application that analyzes text articles using local AI (Ollama) to extract summaries, person names, and categories. All analyses are stored in a SQLite database and can be exported to JSON format.

## Features

- **AI-Powered Text Analysis**: Analyzes articles using local Ollama (Mistral model)
- **Automatic Summary Generation**: Creates 2-3 sentence summaries of any text
- **Named Entity Recognition**: Extracts person names mentioned in the text
- **Category Classification**: Automatically categorizes articles (News, Technology, Sports, Politics, Business, Science, Entertainment, Health, Other)
- **Database Storage**: Saves all analyses in a SQLite database
- **Export to JSON**: Download all analyses as a JSON file (includes summary, category, and persons mentioned)
- **Web Interface**: Simple and easy-to-use web interface

## Prerequisites

Before running this application, you need:

1. **Python 3.7+** installed on your system
2. **Ollama** installed and running locally
3. **Mistral model** downloaded in Ollama

### Installing Ollama and Mistral

1. Install Ollama from: https://ollama.ai
2. Download the Mistral model:
   ```bash
   ollama pull mistral
   ```
3. Verify Ollama is running:
   ```bash
   ollama list
   ```

## Installation

1. Clone or download this repository

2. Install the required Python packages:
   ```bash
   pip install -r requirements.txt
   ```

## Running the Application

1. Make sure Ollama is running on your system

2. Start the Flask application:
   ```bash
   python "app2 best ready.py"
   ```

3. Open your web browser and go to:
   ```
   http://localhost:5000
   ```

## How to Use

### Analyzing Text

1. Open the application in your browser
2. Paste or type your article text in the text area
3. Click the "Analyze" button
4. Wait for the AI to process your text
5. View the results (summary, persons mentioned, category)
6. The analysis is automatically saved to the database

### Exporting to JSON

1. Click the "Export to JSON" button above the "Previous Analyses" table
2. A file named `analyses_export.json` will be downloaded
3. The file contains all saved analyses with:
   - ID
   - Summary
   - Category
   - Persons mentioned
   - Original text

## Project Structure

```
InsightAssistant/
├── app2 best ready.py    # Main Flask application
├── requirements.txt      # Python dependencies
├── db/                   # Database folder
│   └── insight.db       # SQLite database (created automatically)
├── templates/           # HTML templates
│   └── index.html      # Main web interface
├── static/             # Static files (CSS, etc.)
│   └── style.css       # Styling
└── venv/               # Virtual environment (optional)
```

## Technologies Used

- **Flask 3.1.1**: Web framework
- **Flask-SQLAlchemy 3.1.1**: Database ORM
- **SQLAlchemy 2.0.41**: Database toolkit
- **Requests 2.32.4**: HTTP library for Ollama API calls
- **SQLite**: Lightweight database
- **Ollama**: Local AI model server
- **Mistral**: AI language model

## New Features Added

### Export to JSON (Student Project)
- Added `/export` route to the Flask application
- Created export button in the web interface
- Implemented JavaScript functionality to download JSON files
- Exports all analyses with full details

## Database Schema

The application uses a single table called `Analysis`:

- `id`: Primary key (auto-increment)
- `original_text`: The full article text
- `summary`: AI-generated summary
- `persons`: Comma-separated list of person names
- `category`: Article category

## Troubleshooting

### "ModuleNotFoundError: No module named 'flask'"
- Install the requirements: `pip install -r requirements.txt`

### "Failed to call Ollama"
- Make sure Ollama is running: Check http://localhost:11434
- Verify the Mistral model is installed: `ollama list`
- Check if the model name in the code matches your installed model

### The app won't start
- Check if port 5000 is already in use
- Make sure all dependencies are installed
- Verify Python version is 3.7 or higher

## Development Notes

This is a student project created for educational purposes. The application demonstrates:
- Web development with Flask
- Database operations with SQLAlchemy
- API integration (Ollama)
- Frontend JavaScript for dynamic functionality
- File download functionality
- JSON data handling


## License

This project is for educational purposes.
