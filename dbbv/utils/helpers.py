import functools, os
from os import listdir
from os.path import isfile, join
from pathlib import Path
from flask import redirect, session, g, url_for, current_app

ALLOWED_EXTENSIONS = {"db", "sqlite", "sqlite3"}


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for("auth.login"))

        return view(**kwargs)

    return wrapped_view


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def split_ext(filename):
    ext = Path(filename).suffix
    return ext


def check_user_folder():
    # check user folder for safety
    user_folder = session.get("user_folder")
    if not user_folder:
        user_folder = os.path.join(
            current_app.config["UPLOAD_FOLDER"], session.get("username")
        )
        os.makedirs(user_folder, exist_ok=True)
        session["user_folder"] = user_folder

    return user_folder


def is_valid_sqlite(file_obj):
    """
    Check whether the uploaded file is a real SQLite database.

    Reads first 16 bytes and compares to SQLite magic header.
    """
    header = file_obj.read(16)  # Read first 16 bytes
    file_obj.seek(0)  # Reset pointer after reading
    return header == b"SQLite format 3\x00"


def list_user_files():
    files = [
        file
        for file in listdir(session["user_folder"])
        if isfile(join(session["user_folder"], file)) and allowed_file(file)
    ]
    return files
