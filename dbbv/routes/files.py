import os
from flask import(
    Blueprint, flash, g, redirect, render_template, request, 
    session, url_for, current_app, send_from_directory
)
from werkzeug.utils import secure_filename
from dbbv.routes.helpers import allowed_file, login_required, apology 

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
            return redirect(url_for('files.download_file', name=filename))

        return render_template("files.html")
    else:
        return render_template("files.html")


@bp.route('/download/<name>', methods=['GET', 'POST'])
@login_required
def download_file(name):
        return send_from_directory(session["user_folder"], name)