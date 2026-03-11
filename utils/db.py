import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "app.db")


def _connect():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)   # fresh connection per call — thread safe
    conn.row_factory = sqlite3.Row
    return conn


# -----------------------------
# Initialize Database
# -----------------------------
def init_db():
    with _connect() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS tests (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                filename   TEXT,
                predicted  TEXT,
                confidence REAL,
                crop_type  TEXT,
                actual     TEXT,
                correct    INTEGER,
                timestamp  TEXT
            )
        """)
        conn.commit()


# -----------------------------
# Add New Prediction Record
# -----------------------------
def add_test(filename, predicted, confidence, actual=None, crop_type=None):

    ts = datetime.utcnow().isoformat()

    if actual == "NULL" or actual == "":
        actual = None

    correct = None

    if actual is not None:
        predicted_clean = (
            predicted
            .replace("Potato___", "")
            .replace("Tomato__", "")   # double underscore FIRST
            .replace("Tomato_",  "")
            .replace("_", " ")
            .lower().strip()
        )
        correct = 1 if predicted_clean == actual.lower().strip() else 0

    with _connect() as conn:
        conn.execute(
            """
            INSERT INTO tests
            (filename, predicted, confidence, crop_type, actual, correct, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (filename, predicted, confidence, crop_type, actual, correct, ts),
        )
        conn.commit()


# -----------------------------
# Get All Tests (History)
# -----------------------------
def get_all_tests():
    with _connect() as conn:
        rows = conn.execute("SELECT * FROM tests ORDER BY id DESC").fetchall()
    return [dict(r) for r in rows]


# -----------------------------
# Get Single Test
# -----------------------------
def get_test_by_id(test_id):
    with _connect() as conn:
        row = conn.execute("SELECT * FROM tests WHERE id = ?", (test_id,)).fetchone()
    return dict(row) if row else None


# -----------------------------
# Helper: clean a raw class name
# -----------------------------
def _clean(c):
    return (
        c.replace("Potato___", "")
         .replace("Tomato__",  "")   # double FIRST
         .replace("Tomato_",   "")
         .replace("_", " ")
         .strip()
    )


# -----------------------------
# Overall Dashboard Statistics
# -----------------------------
def get_stats(class_names):

    with _connect() as conn:

        total             = conn.execute("SELECT COUNT(*) as n FROM tests").fetchone()["n"]
        potato_tests      = conn.execute("SELECT COUNT(*) as n FROM tests WHERE lower(crop_type)='potato'").fetchone()["n"]
        tomato_tests      = conn.execute("SELECT COUNT(*) as n FROM tests WHERE lower(crop_type)='tomato'").fetchone()["n"]
        total_with_actual = conn.execute("SELECT COUNT(*) as n FROM tests WHERE actual IS NOT NULL").fetchone()["n"]
        correct           = conn.execute("SELECT COUNT(*) as n FROM tests WHERE correct=1").fetchone()["n"]
        avg_row           = conn.execute("SELECT AVG(confidence) as a FROM tests").fetchone()["a"]

        per_class = {}
        for c in class_names:
            clean = _clean(c)
            predicted_count      = conn.execute("SELECT COUNT(*) as n FROM tests WHERE predicted=?", (c,)).fetchone()["n"]
            correct_for_class    = conn.execute("SELECT COUNT(*) as n FROM tests WHERE lower(actual)=lower(?) AND correct=1", (clean,)).fetchone()["n"]
            total_actual_for_cls = conn.execute("SELECT COUNT(*) as n FROM tests WHERE lower(actual)=lower(?)", (clean,)).fetchone()["n"]
            per_class[c] = {
                "predicted_count":        predicted_count,
                "correct_for_class":      correct_for_class,
                "total_actual_for_class": total_actual_for_cls,
                "clean_name":             clean,
            }

    accuracy       = round((correct / total_with_actual) * 100, 2) if total_with_actual else None
    avg_confidence = round(avg_row * 100, 2) if avg_row else None

    return {
        "total":             total,
        "potato_tests":      potato_tests,
        "tomato_tests":      tomato_tests,
        "total_with_actual": total_with_actual,
        "correct":           correct,
        "accuracy":          accuracy,
        "avg_confidence":    avg_confidence,
        "per_class":         per_class,
    }


# -----------------------------
# Per-Crop Statistics (Potato or Tomato)
# Used by the dashboard API for per-tab breakdown
# -----------------------------
def get_crop_stats(crop_type: str, crop_class_names: list):
    """
    Same shape as get_stats() but filtered to one crop type.
    crop_type:        'potato' or 'tomato'
    crop_class_names: the class list for that crop from predict.py
    """
    ct = crop_type.lower()

    with _connect() as conn:

        total             = conn.execute("SELECT COUNT(*) as n FROM tests WHERE lower(crop_type)=?", (ct,)).fetchone()["n"]
        total_with_actual = conn.execute("SELECT COUNT(*) as n FROM tests WHERE lower(crop_type)=? AND actual IS NOT NULL", (ct,)).fetchone()["n"]
        correct           = conn.execute("SELECT COUNT(*) as n FROM tests WHERE lower(crop_type)=? AND correct=1", (ct,)).fetchone()["n"]
        avg_row           = conn.execute("SELECT AVG(confidence) as a FROM tests WHERE lower(crop_type)=?", (ct,)).fetchone()["a"]

        per_class = {}
        for c in crop_class_names:
            clean = _clean(c)
            predicted_count      = conn.execute("SELECT COUNT(*) as n FROM tests WHERE predicted=? AND lower(crop_type)=?", (c, ct)).fetchone()["n"]
            correct_for_class    = conn.execute("SELECT COUNT(*) as n FROM tests WHERE lower(actual)=lower(?) AND correct=1 AND lower(crop_type)=?", (clean, ct)).fetchone()["n"]
            total_actual_for_cls = conn.execute("SELECT COUNT(*) as n FROM tests WHERE lower(actual)=lower(?) AND lower(crop_type)=?", (clean, ct)).fetchone()["n"]
            per_class[c] = {
                "predicted_count":        predicted_count,
                "correct_for_class":      correct_for_class,
                "total_actual_for_class": total_actual_for_cls,
                "clean_name":             clean,
            }

    accuracy       = round((correct / total_with_actual) * 100, 2) if total_with_actual else None
    avg_confidence = round(avg_row * 100, 2) if avg_row else None

    return {
        "total":             total,
        "total_with_actual": total_with_actual,
        "correct":           correct,
        "accuracy":          accuracy,
        "avg_confidence":    avg_confidence,
        "per_class":         per_class,
    }