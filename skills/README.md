# Antigravity Skills for Subtext AI

This directory contains "skills" - standalone scripts that encapsulate key capabilities of the Subtext AI project.

## Available Skills

### 1. `generate_data.py`
Generates synthetic WhatsApp-style chat data for testing.
**Usage:**
```bash
python skills/generate_data.py --output data/my_chat.txt --count 50
```

### 2. `run_server.py`
Starts the FastAPI backend server.
**Usage:**
```bash
python skills/run_server.py
```
Access the API docs at http://127.0.0.1:8000/docs.

### 3. `analyze.py`
Analyzes a chat log file for conversational dissonance using the trained model.
**Usage:**
```bash
python skills/analyze.py --file data/my_chat.txt
```
Outputs a summary to console and a CSV file with full results.
