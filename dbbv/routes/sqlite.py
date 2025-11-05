from os import listdir
from os.path import isfile, join
from flask import(
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
import sqlite3
    
from dbbv.db import get_db, query_db, execute_db
from dbbv.routes.helpers import apology, login_required

bp = Blueprint('sqlite', __name__)

@bp.route("/", methods=['GET', 'POST'])
@login_required
def index():
    files = [file for file in listdir(session["user_folder"]) if isfile(join(session["user_folder"], file))]
    if not session.get('paired_queries'):
        session['paired_queries'] = []

    if request.method == 'POST':
        # Run the query
        if request.form.get("action") == "run" and request.form.get("query"):
            query = request.form.get("query")
            query_result = """1|1|665.92|NFLX|2025-10-23 13:31:01|Buy|1
            2|10|261.8|FL|2025-10-23 13:31:06|Buy|1
            3|1|661.92|NFLX|2025-10-23 16:22:15|Buy|1
            4|1|664.94|NFLX|2025-10-23 16:39:26|Buy|1
            5|1|662.14|NFLX|2025-10-23 16:39:40|Sell|1
            6|1|661.59|NFLX|2025-10-23 17:04:00|Buy|1
            7|1|666.05|NFLX|2025-10-24 01:05:39|Buy|1
            8|1|670.06|NFLX|2025-10-24 01:21:49|Sell|1
            9|1|666.63|NFLX|2025-10-24 01:22:04|Sell|1
            10|2|1337.44|NFLX|2025-10-24 01:22:13|Sell|1
            11|1|26.28|FL|2025-10-24 01:22:17|Sell|1
            12|1|26.23|FL|2025-10-24 01:22:21|Buy|1"""
            session['paired_queries'] += [(query, query_result)]           
            print(session['paired_queries'])
        # Clear queries
        elif request.form.get("action") == "clear":
            session['paired_queries'] = []
        elif request.form.get("remove"):
            session['paired_queries'].pop(int(request.form.get("remove")))
        
    if request.method == 'GET':
        pass

    return render_template("index.html", files=files, db_selected=session['db_selected'],
                           paired_queries=session['paired_queries']) 

def get_db_sqlite():
    db_path = session['db_selected']
    if 'custom_db' not in g or g.get('custom_db_path') != db_path:
        g.custom_db = sqlite3.connect(
            db_path,
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.custom_db.row_factory = sqlite3.Row
        g.custom_db.set_trace_callback(print)
    return g.custom_db

def close_custom_db(e=None):
    db = g.pop('custom_db', None)
    if db is not None:
        db.close()

