import os
import sqlite3
from flask import (
    Blueprint,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for,
    send_from_directory,
    jsonify,
)
from werkzeug.utils import secure_filename
from dbbv.utils.helpers import (
    allowed_file,
    login_required,
    ALLOWED_EXTENSIONS,
    is_valid_sqlite,
    check_user_folder,
    list_user_files,
)
from dbbv.user_db.user_sqlite import query_db_sqlite

bp = Blueprint("files", __name__)


@bp.route("/upload", methods=["GET", "POST"])
@login_required
def upload():
    check_user_folder()
    if session.get("db_selected"):
        schemas = query_db_sqlite("SELECT * FROM sqlite_master")
    else:
        schemas = None
    if request.method == "POST":
        # check if the post request has the file part
        if "file" not in request.files:
            flash("No file part", "dark")
            return redirect(request.url)
        file = request.files["file"]
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == "":
            flash("No selected file", "dark")
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            if not filename:
                flash("invalid filename", "dark")
                return redirect(request.url)
            if not is_valid_sqlite(file):
                flash("file is not sqlite db", "dark")
                return redirect(request.url)
            filepath = os.path.join(session["user_folder"], filename)
            if os.path.exists(filepath):
                flash(
                    "A file with that name already exists. Please rename it and try again.",
                    "dark",
                )
                return redirect(request.url)
            file.save(filepath)
        else:
            flash("file (extension) error, wrong file extension", "dark")

    files = list_user_files()
    return render_template(
        "files.html", files=files, db_selected=session["db_selected"], schemas=schemas
    )


@bp.route("/download/<name>", methods=["GET"])
@login_required
def download_file(name):
    user_folder = check_user_folder()
    filename = secure_filename(name.strip())
    if not filename or not user_folder:
        flash("Invalid download request", "dark")
        return redirect(url_for("sqlite.index"))
    if not allowed_file(filename):
        flash("Not allowed to download this file", "danger")
        return redirect(url_for("sqlite.index"))

    # ensure the file exists inside user folder
    filepath = os.path.join(user_folder, filename)
    if not os.path.exists(filepath):
        flash("File not found", "dark")
        return redirect(url_for("sqlite.index"))
    return send_from_directory(user_folder, filename)


@bp.route("/select", methods=["POST"])
@login_required
def select():
    check_user_folder()
    filename = request.form.get("selected_file")
    if not filename:
        error = "Invalid db selected"
        return jsonify({"error": str(error)}), 400
    filename = secure_filename(filename)

    if not allowed_file(filename):
        error = "Invalid file type"
        return jsonify({"error": error}), 400

    if not os.path.isfile(os.path.join(session["user_folder"], filename)):
        error = "file doesn't exist"
        return jsonify({"error": error}), 400

    session["db_selected"] = filename
    try:
        schemas = query_db_sqlite("SELECT * FROM sqlite_master")
        return jsonify(schemas)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp.route("/remove", methods=["POST"])
@login_required
def removeFile():
    check_user_folder()

    filename = secure_filename(request.form.get("remove", "").strip())
    if not filename:
        flash("No File specified", "dark")
        return redirect(url_for("sqlite.index"))

    if not allowed_file(filename):
        flash("Specified file not allowed to be removed", "dark")
        return redirect(url_for("sqlite.index"))

    filepath = os.path.join(session["user_folder"], filename)
    if os.path.exists(filepath):
        os.remove(filepath)
        if filename == session.get("db_selected"):
            session["db_selected"] = None
            flash("selected db deleted", "success")
    else:
        flash("The file does not exist", "dark")

    files = list_user_files()
    if not files:
        flash("Last file deleted", "dark")
        session["db_selected"] = None
    return redirect(url_for("sqlite.index"))


@bp.route("/create", methods=["POST"])
@login_required
def create():
    check_user_folder()
    filename = request.form.get("filename", "").strip()
    if not filename:
        flash("No filename entered", "dark")
        return redirect(url_for("files.upload"))
    extension = request.form.get("extension")
    if not extension:
        flash("no extension selected")
        return redirect(url_for("files.upload"))
    filename = secure_filename(filename)
    if not filename or filename == "":
        flash("invalid filename", "dark")
        return redirect(url_for("files.upload"))
    if not extension in ALLOWED_EXTENSIONS:
        flash("extension not allowed", "dark")
        return redirect(url_for("files.upload"))

    # adding extension to filename
    filename = f"{filename}.{extension}"

    filepath = os.path.join(session["user_folder"], filename)
    if os.path.exists(filepath):
        flash("A file with that name already Exists.", "dark")
        return redirect(url_for("files.upload"))

    try:
        sqlite3.connect(filepath).close()
        flash("file created successfully!", "success")
    except Exception as e:
        flash(f"error creating file: {e}", "dark")
        return redirect(url_for("files.upload"))
    return redirect(url_for("files.upload"))
