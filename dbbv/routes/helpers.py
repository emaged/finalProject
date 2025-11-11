from flask import redirect, render_template, session, g, url_for
import functools
from pathlib import Path

ALLOWED_EXTENSIONS = {'db', 'sqlite', 'sqlite3'}

def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def split_ext(filename):
    ext = Path(filename).suffix
    return ext