# Promptly - AI Content Generation Platform

A modern, full-stack AI content generation web application built with React + Vite (frontend) and FastAPI (backend).

## Features

- Multi-platform content generation (General, Instagram, LinkedIn, YouTube Script)
- Intent classification
- Sentiment analysis
- Semantic document retrieval
- HuggingFace model integration
- Fallback handling for API failures
- Clean, modular architecture

## Project Structure

```
Promptly/
├── backend/
│   ├── __init__.py
│   ├── main.py
│   ├── models.py
│   ├── prompt_builder.py
│   ├── hf_client.py
│   ├── classifiers.py
│   ├── retriever.py
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Generator.jsx
│   │   │   └── Output.jsx
│   │   ├── services/
│   │   │   └── api.js
│   │   ├── App.jsx
│   │   ├── App.css
│   │   ├── main.jsx
│   │   └── index.css
│   ├── index.html
│   ├── package.json
│   └── vite.config.js
├── .env.example
└── README.md
```

## Setup Instructions

### Prerequisites

- Python 3.9+
- Node.js 18+
- HuggingFace API Token

### Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Create a `.env` file in the backend directory:
```
HF_TOKEN=your_huggingface_token_here
```

Run the backend:
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

The frontend will be available at `http://localhost:5173`

## API Endpoints

### POST /generate

Request body:
```json
{
  "text": "Your content idea",
  "platform": "Instagram",
  "temperature": 0.7,
  "max_tokens": 256,
  "use_legacy": false
}
```

Response:
```json
{
  "content": "Generated content...",
  "intent": "informational",
  "sentiment": "positive",
  "documents": ["doc1", "doc2", "doc3"],
  "time_taken": 1.23,
  "fallback_used": false,
  "reason": null
}
```

## License

MIT

