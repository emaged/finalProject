import os
import json


def history_file_for(user_folder):
    return os.path.join(user_folder, "query_history.json")


def load_history(user_folder):
    path = history_file_for(user_folder)
    if not os.path.exists(path):
        return []
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


def save_history(user_folder, history):
    path = history_file_for(user_folder)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(history, f)