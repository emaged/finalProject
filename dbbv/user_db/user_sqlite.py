import os
from flask import(
    g, session, current_app
)
import sqlite3


def dict_factory(cursor, row):
    fields = [column[0] for column in cursor.description]
    return {key: value for key, value in zip(fields, row)}


def get_db_sqlite():
    db_path = os.path.join(session['user_folder'], session['db_selected'])
    if 'custom_db' not in g or g.get('custom_db_path') != db_path:
        g.custom_db = sqlite3.connect(
            db_path,
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.custom_db.row_factory = dict_factory
        if current_app.debug:
            g.custom_db.set_trace_callback(print)
        
        # ENABLE FOREIGN KEY ENFORCEMENT 
        g.custom_db.execute("PRAGMA foreign_keys = ON")
        
        # Keep track of what DB this connection belongs to
        g.custom_db_path = db_path

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
    
    if query.strip().lower().startswith('select'):
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