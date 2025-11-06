from flask import redirect, render_template, session, g, url_for
import functools
from pathlib import Path

LLOWED_EXTENSIONS = {'db', 'sqlite', 'sqlite3'}

def apology(message, code=400):
    """Render message as an apology to user."""

    def escape(s):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [
            ("-", "--"),
            (" ", "-"),
            ("_", "__"),
            ("?", "~q"),
            ("%", "~p"),
            ("#", "~h"),
            ("/", "~s"),
            ('"', "''"),
        ]:
            s = s.replace(old, new)
        return s

    return render_template("apology.html", top=code, bottom=escape(message)), code

def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            #print("no user in login_required")
            return redirect(url_for('auth.login'))

        #print(f"user in login_required {g.user['username']}")
        return view(**kwargs)

    return wrapped_view

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def split_ext(filename):
    ext = Path(filename).suffix
    return ext