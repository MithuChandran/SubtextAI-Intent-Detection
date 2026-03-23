# SubtextAI 🚀

**SubtextAI** is a sophisticated AI-powered conversational analysis tool designed to decode the "subtext" of digital communications. It specialized in detecting intent and conversational dynamics in chat logs (such as WhatsApp), providing deep insights through a modern, interactive dashboard.

---

## 🌟 Key Features

- **30-Class Intent Classification**: Leverages a fine-tuned RoBERTa transformer model to classify messages into 30 distinct conversational intents.
- **Dissonance Detection**: Heuristic-based analysis to identify conversational "friction" or dissonance in long-form chats.
- **Batch Optimization**: Efficiently processes thousands of messages using optimized PyTorch pipelines.
- **Interactive Dashboard**: Clean, premium UI featuring:
  - Message-by-message intent breakdown.
  - Overall conversational statistics.
  - Interactive charts for intent distribution.
  - System health monitoring.
- **Flexible UI**: Built with a "dark-mode first" aesthetic for a professional, focused user experience.

---

## 🛠️ Technology Stack

### Backend (The Brain)
- **Language**: Python 3.12
- **Framework**: FastAPI
- **AI/ML**: PyTorch, Hugging Face Transformers
- **Deployment**: Hugging Face Spaces (Docker-based)

### Frontend (The Face)
- **Framework**: React.js (Vite)
- **Styling**: Vanilla CSS (Modern, premium theme)
- **Icons**: Lucide React
- **Deployment**: Vercel

---

## 📂 Project Structure

```text
SubtextAI/
├── src/            # Backend source code (FastAPI)
│   ├── model/      # AI model interfaces and logic
│   ├── parser/     # Chat log parsing (WhatsApp format)
│   └── api/        # API route definitions
├── ui/             # Frontend source code (React)
│   ├── src/        # UI components and services
│   └── public/     # Static assets
├── skills/         # Standalone scripts for key capabilities
├── scripts/        # Utility scripts for training and data prep
├── models/         # (Local only) Model weight placeholders
├── requirements.txt # Python dependencies
└── Dockerfile       # Deployment configuration
```

---

## 🚀 Getting Started

### 1. Local Backend Setup
```bash
# Create a virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the server
$env:PYTHONPATH="."
uvicorn src.main:app --host 0.0.0.0 --port 8000
```
Access docs at: `http://localhost:8000/docs`

### 2. Local Frontend Setup
```bash
cd ui
npm install
npm run dev
```
Access site at: `http://localhost:5173`

---

## 🛠️ Standalone Skills (CLI)

The `skills/` directory contains standalone scripts for command-line power users:

### `generate_data.py`
Generates synthetic WhatsApp-style chat data for testing purposes.
```bash
python skills/generate_data.py --output data/my_chat.txt --count 50
```

### `run_server.py`
Quick-start script for the FastAPI backend server.
```bash
python skills/run_server.py
```

### `analyze.py`
Analyzes a chat log file for conversational dissonance directly in your terminal.
```bash
python skills/analyze.py --file data/my_chat.txt
```

---

## 🌐 Deployment

This project is optimized for a hybrid cloud architecture:
- **Model Hosting**: Large model weights are hosted on the **Hugging Face Model Hub**.
- **Backend API**: Hosted on **Hugging Face Spaces** as a Docker container.
- **Frontend App**: Hosted on **Vercel** for high-performance delivery.

---

## 📝 Author
Developed as a Final Year Project (FYP).

*Note: Large model files are excluded from this repository and are loaded dynamically from the Hugging Face Hub during runtime.*
