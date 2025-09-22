# Book Recommending - Development Setup

## Prerequisites
- Python 3.13 (project includes a `venv/` already, but you may recreate)
- pip

## Setup

```bash
# From the project root
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Create .env (or copy from .env.example if present)
cat > .env <<'EOF'
FLASK_RUN_HOST=0.0.0.0
FLASK_RUN_PORT=5000
FLASK_DEBUG=1
EOF
```

## Run (development)

```bash
python app.py
```

- App: http://localhost:5000
- Health: http://localhost:5000/health

## Run (with Gunicorn)

```bash
gunicorn -w 2 -b 0.0.0.0:5000 app:app
```

## Notes
- Ensure `popular.pkl`, `pt.pkl`, `books.pkl`, `similarity_scores.pkl` exist alongside `app.py`.
- Title matching is exact; enter a title that exists in the dataset.
