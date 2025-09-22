from flask import Flask, render_template ,request, jsonify
import numpy as np
import pickle
import os
from pathlib import Path

try:
    from dotenv import load_dotenv  # type: ignore
    load_dotenv()
except Exception:
    # dotenv is optional in production
    pass

app = Flask(__name__)

# Resolve data directory relative to this file to avoid CWD issues
BASE_DIR = Path(__file__).resolve().parent


def safe_pickle_load(file_path: Path):
    with open(file_path, 'rb') as f:
        return pickle.load(f)


try:
    popular_df = safe_pickle_load(BASE_DIR / 'popular.pkl')
    pt = safe_pickle_load(BASE_DIR / 'pt.pkl')
    books = safe_pickle_load(BASE_DIR / 'books.pkl')
    similarity_scores = safe_pickle_load(BASE_DIR / 'similarity_scores.pkl')
except FileNotFoundError as exc:
    # Surface clear error at startup if model artifacts are missing
    missing = str(exc).split("[")[-1].rstrip(")'") if exc else 'required file'
    raise RuntimeError(f"Required data file missing: {missing}. Ensure the *.pkl files exist next to app.py") from exc
except Exception as exc:
    raise RuntimeError("Failed to load data artifacts. Verify pickle files' compatibility and integrity.") from exc

@app.route('/')
def home():
    return render_template("index.html" ,book_name = list(popular_df['Book-Title'].values),
    author=list(popular_df['Book-Author'].values),
    image=list(popular_df['Image-URL-M'].values),
    votes= list(popular_df['num_ratings'].values),
    rating=[round( i , 2) for i in popular_df['avg_rating'].values]
    )
@app.route('/recommend')
def recommend_ui():
    return render_template('recommend.html')

@app.route('/recommend_books',methods=['post'])
def recommend():
    user_input = (request.form.get('user_input') or '').strip()
    if not user_input:
        return render_template('recommend.html', data=[], error='Please enter a book title.')

    try:
        indices = np.where(pt.index == user_input)[0]
        if len(indices) == 0:
            return render_template('recommend.html', data=[], error=f'No exact match found for "{user_input}".')

        index = int(indices[0])
        similar_items = sorted(
            list(enumerate(similarity_scores[index])), key=lambda x: x[1], reverse=True
        )[1:9]

        data = []
        for i in similar_items:
            item = []
            temp_df = books[books['Book-Title'] == pt.index[i[0]]]
            temp_df = temp_df.drop_duplicates('Book-Title')
            item.extend(list(temp_df['Book-Title'].values))
            item.extend(list(temp_df['Book-Author'].values))
            item.extend(list(temp_df['Image-URL-M'].values))
            data.append(item)

        return render_template('recommend.html', data=data, query=user_input)
    except Exception as exc:
        return render_template('recommend.html', data=[], error='Unexpected error. Try another title.'), 500


@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "ok"})

if __name__ == '__main__':
    host = os.getenv('FLASK_RUN_HOST', '0.0.0.0')
    try:
        port = int(os.getenv('FLASK_RUN_PORT', os.getenv('PORT', '5000')))
    except ValueError:
        port = 5000
    debug_env = os.getenv('FLASK_DEBUG', '1')
    debug = debug_env in ('1', 'true', 'True', 'yes', 'on')
    app.run(host=host, port=port)