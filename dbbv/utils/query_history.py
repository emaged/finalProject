import os
import json

MAX_HISTORY_ITEMS = 30
MAX_RESULT_ROWS = 100


def load_history(user_folder):
    path = os.path.join(user_folder, "query_history.json")
    if not os.path.exists(path):
        return []

    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


def save_history(user_folder, history):
    while len(history) > MAX_HISTORY_ITEMS:
        history.pop()  # remove oldest

    filepath = os.path.join(user_folder, "query_history.json")
    with open(filepath, "w", encoding="utf8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2, default=str)

    return history
