import os
from os import listdir
from os.path import isfile, join
from flask import(
    Blueprint, flash, g, redirect, render_template, request, 
    session, url_for, current_app, send_from_directory, jsonify
)
from werkzeug.utils import secure_filename
from dbbv.routes.helpers import allowed_file, login_required, apology 
from dbbv.routes.sqlite import query_db_sqlite

UPLOAD_FOLDER = 'user_databases'

bp = Blueprint('files', __name__)

@bp.route('/upload', methods=['GET', 'POST'])
@login_required
def files():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(session["user_folder"], filename)
            if os.path.exists(filepath):
                flash('A file with that name already exists. Please rename it and try again.')
                return redirect(request.url)
            file.save(filepath)
            print(filepath)
        else:
            flash("file (extension) error, wrong file extension")

    files = [file for file in listdir(session["user_folder"]) if isfile(join(session["user_folder"], file))]
    return render_template("files.html", files=files, db_selected=session["db_selected"], schemas=session['schemas'])


@bp.route('/download/<name>', methods=['GET'])
@login_required
def download_file(name):
    print(name)
    return send_from_directory(session["user_folder"], name)

@bp.route('/select', methods=['POST'])
@login_required
def select():
    data = request.form.get("selected_file")
    session["db_selected"] = data
    try:
        schemas = query_db_sqlite("SELECT * FROM sqlite_master")
        return jsonify(schemas)
    except Exception as e:
        flash(e)
        print(e)
        return jsonify({"error", str(e)}), 500
    
     
@bp.route('/remove', methods=['POST'])
@login_required
def removeFile():
    filename = request.form.get("remove")
    filepath = os.path.join(session["user_folder"], filename)
    if filepath:
        os.remove(filepath)
        if filename is session["db_selected"]:
            session["db_selected"] = None
            session['schemas'] = None
            flash("selected db deleted")

    else:
        print("The file does not exist")
    files = [file for file in listdir(session['user_folder']) if isfile(join(session["user_folder"], file))]
    if not files:
        flash("Last file deleted")
        session["db_selected"] = None
        session['schemas'] = None
    return redirect(url_for('sqlite.index'))
