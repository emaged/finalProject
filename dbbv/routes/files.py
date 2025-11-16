import os, sqlite3
from os import listdir
from os.path import isfile, join
from flask import(
    Blueprint, flash, g, redirect, render_template, request, 
    session, url_for, current_app, send_from_directory, jsonify
)
from werkzeug.utils import secure_filename
from dbbv.routes.helpers import allowed_file, login_required, ALLOWED_EXTENSIONS
from dbbv.routes.sqlite_routes import query_db_sqlite

bp = Blueprint('files', __name__)

@bp.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    # check user folder for safety
    user_folder = session.get('user_folder')
    if not user_folder:
        user_folder = os.path.join(current_app.config['UPLOAD_FOLDER'], session.get('username'))
        os.makedirs(user_folder, exist_ok=True)
        session['user_folder'] = user_folder

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
            if not filename:
                flash('invalid filename')
                return redirect(request.url)
            if not is_valid_sqlite(file):
                flash('file is not sqlite db')
                return redirect(request.url)
            filepath = os.path.join(session['user_folder'], filename)
            if os.path.exists(filepath):
                flash('A file with that name already exists. Please rename it and try again.')
                return redirect(request.url)
            file.save(filepath)
        else:
            flash('file (extension) error, wrong file extension')

    files = [file for file in listdir(session['user_folder']) if isfile(join(session['user_folder'], file)) and allowed_file(file)]
    return render_template('files.html', files=files, db_selected=session['db_selected'], schemas=session['schemas'])


@bp.route('/download/<name>', methods=['GET'])
@login_required
def download_file(name):
    filename = secure_filename(name)
    user_folder = session.get('user_folder')
    if not filename or not user_folder:
        flash('Invalid download request')
        return redirect(url_for('sqlite.index'))
   
    # ensure the file exists inside user folder
    filepath = os.path.join(user_folder, filename)
    if not os.path.exists(filepath):
        flash('File not found')
        return redirect(url_for('sqlite.index'))
    return send_from_directory(user_folder, filename)


@bp.route('/select', methods=['POST'])
@login_required
def select():
    filename = request.form.get('selected_file')
    if not filename:
        error = 'Invalid db selected'
        flash(error)
        return jsonify({'error': str(error)}), 400
    filename = secure_filename(filename)

    if not allowed_file(filename):
        error = 'Invalid file type'
        flash(error)
        return jsonify({'error': error}), 400
    session['db_selected'] = filename 
    try:
        schemas = query_db_sqlite('SELECT * FROM sqlite_master')
        session['schemas'] = schemas
        return jsonify(schemas)
    except Exception as e:
        flash(e)
        return jsonify({'error': str(e)}), 500
    
     
@bp.route('/remove', methods=['POST'])
@login_required
def removeFile():
    filename = secure_filename(request.form.get('remove'))
    if not filename:
        flash('No File specified')
        return redirect(url_for('sqlite.index'))

    filepath = os.path.join(session['user_folder'], filename)
    if os.path.exists(filepath):
        os.remove(filepath)
        print(filename)
        if filename == session.get('db_selected'):
            session['db_selected'] = None
            session['schemas'] = None
            flash('selected db deleted')
    else:
        flash('The file does not exist')

    files = [file for file in listdir(session['user_folder']) if isfile(join(session['user_folder'], file))]
    if not files:
        flash('Last file deleted')
        session['db_selected'] = None
        session['schemas'] = None
    return redirect(url_for('sqlite.index'))


@bp.route('/create', methods=['POST'])
@login_required
def create():    
    # check user folder for safety
    user_folder = session.get('user_folder')
    if not user_folder:
        user_folder = os.path.join(current_app.config['UPLOAD_FOLDER'], session.get('username'))
        os.makedirs(user_folder, exist_ok=True)
        session['user_folder'] = user_folder
    
    filename = request.form.get('filename','').strip()
    if not filename:
        flash('No filename entered')
        return redirect(url_for('files.upload'))
    extension = request.form.get('extension')
    if not extension:
        flash('no extension selected') 
        return redirect(url_for('files.upload')) 
    filename = secure_filename(filename)
    if not filename or filename == '':
        flash('invalid filename')
        return redirect(url_for('files.upload'))
    if not extension in ALLOWED_EXTENSIONS:
        flash("extension not allowed")
        return redirect(url_for('files.upload'))

    # adding extension to filename 
    filename = f"{filename}.{extension}"

    filepath = os.path.join(session['user_folder'], filename)
    if os.path.exists(filepath):
        flash('A file with that name already Exists.')
        return redirect(url_for('files.upload'))
    
    try:
        sqlite3.connect(filepath).close()
        flash('file created successfully!')
    except Exception as e:
        flash(f'error creating file: {e}')
        return redirect(url_for('files.upload'))
    return redirect(url_for('files.upload'))

def is_valid_sqlite(file_obj):
    """
    Check whether the uploaded file is a real SQLite database.

    Reads first 16 bytes and compares to SQLite magic header.
    """
    header = file_obj.read(16)     # Read first 16 bytes
    print(header)
    file_obj.seek(0)               # Reset pointer after reading
    return header == b"SQLite format 3\x00"
