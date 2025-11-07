import os
from os import listdir
from os.path import isfile, join
from flask import(
    Blueprint, flash, g, redirect, render_template, request, session, url_for, current_app
)
import sqlite3
from dbbv.routes.helpers import apology, login_required, allowed_file

bp = Blueprint('sqlite', __name__)

@bp.route('/', methods=['GET', 'POST'])
@login_required
def index():
    user_folder = session.get('user_folder')
    if not user_folder or not os.path.isdir(user_folder):
        # create user folder if it doesn't exist
        user_folder = os.path.join(current_app.config['UPLOAD_FOLDER'], session.get('username'))
        os.makedirs(user_folder, exist_ok=True)
        session['user_folder'] = user_folder

    files = [file for file in listdir(session['user_folder']) if isfile(join(session["user_folder"], file)) and allowed_file(file)]
    if session.get('db_selected'):
        session['schemas'] = query_db_sqlite("SELECT * FROM sqlite_master")
    
    if request.method == 'POST':
        # Run the query
        if request.form.get('action') == 'run' and request.form.get('query'):
            if not session.get('db_selected'):
                flash("No database selected")
                return redirect(url_for('sqlite.index'))
            query = request.form.get('query')
            try:
                query_result = combined_exec_db_sqlite(query, commit=True)
                header, formatted_result = format_query_result(query_result)
            except Exception as e:
                flash(e)
                return redirect(url_for('sqlite.index'))

            session['paired_queries'] = [(query, header, formatted_result)] + session['paired_queries']           
            print(session['paired_queries'])
        # Clear queries
        elif request.form.get('action') == 'clear':
            session['paired_queries'] = []
        elif request.form.get("remove"):
            popIndex = int(request.form.get("remove"))
            print(popIndex)
            session['paired_queries'].pop(popIndex)
            if not session['paired_queries']:
                return '1'
            else:
                return '0'

    # replace with session.get in production code for safety 
    return render_template('index.html', files=files, db_selected=session['db_selected'],
                           paired_queries=session['paired_queries'], schemas=session['schemas']) 


def dict_factory(cursor, row):
    fields = [column[0] for column in cursor.description]
    return {key: value for key, value in zip(fields, row)}


def get_db_sqlite():
    db_path = os.path.join(session['user_folder'], session['db_selected'])
    print("Opening database:", os.path.abspath(db_path))
    if 'custom_db' not in g or g.get('custom_db_path') != db_path:
        g.custom_db = sqlite3.connect(
            db_path,
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.custom_db.row_factory = dict_factory
        if current_app.debug:
            g.custom_db.set_trace_callback(print)
    return g.custom_db


def close_custom_db(e=None):
    db = g.pop('custom_db', None)
    if db is not None:
        db.close()
        

def query_db_sqlite(query, args=(), one=False):
    cur = get_db_sqlite().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv

def execute_db_sqlite(query, args=()):
    db = get_db_sqlite()
    cur = db.execute(query, args)
    db.commit()
    cur.close()

def combined_exec_db_sqlite(query, args=(), one=False, commit=False):
    db = get_db_sqlite()
    cur = db.execute(query, args)
    result = None
    
    if query.strip().lower().startswith("select"):
        rows = cur.fetchall()
        result = (rows[0] if rows else None) if one else rows
    else:
        if commit:
            db.commit()
    cur.close()
    return result

def format_query_result(query_result):
    if not query_result:
        return [], []
    headers = list(query_result[0].keys())
    return headers, query_result