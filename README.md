# movie_analyze

Movie review and movie data analysis system (Flask + SQLite + Chart.js).

## 1. Requirements

- Python 3.10+ (validated on Python 3.13)
- pip

## 2. Clone

```bash
git clone <repo-url>
cd movie_analyze
```

## 3. Install dependencies

```bash
pip install -r requirements.txt
```

## 4. Run

```bash
python main.py
```

Open:

- `http://127.0.0.1:5000`

## 5. Sentiment model

- Fixed model: `lxyuan/distilbert-base-multilingual-cased-sentiments-student`
- Loaded with `local_files_only=True` (local cache/path only, no proxy needed)

## 6. Notes

- `database.db` is ignored by default.
- On first run, base tables are created automatically.
- For full analysis features, prepare and import business data tables.
