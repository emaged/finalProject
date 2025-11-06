import os
import sqlite3
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, current_app
)
from werkzeug.security import check_password_hash, generate_password_hash
from re import fullmatch
from dbbv.db import get_db, query_db, execute_db
from dbbv.routes.helpers import apology, login_required
    
USERNAME_RE = r'^[A-Za-z0-9_-]{3,30}$'
PASSREG = r"""^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$"""


bp = Blueprint('auth', __name__)

@bp.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = query_db(
            "SELECT * FROM users WHERE username = ?", (request.form.get("username"),)
        )

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0]["password_hash"], request.form.get("password")
        ):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]
        session["username"] = rows[0]["username"]
        user_folder = os.path.join(current_app.config["UPLOAD_FOLDER"], rows[0]["username"])
        session["user_folder"] = user_folder 
        os.makedirs(user_folder, exist_ok=True)
        session["db_selected"] = None
        session['paired_queries'] = []
        session['schemas'] = []
        # Redirect user to home page
        if request.form.get("remember"):
            session.permanent = True 
        else:
            session.permanent = False
        
        return redirect(url_for('sqlite.index'))

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")
    
@bp.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect(url_for('sqlite.index'))

@bp.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    # User reached via Post
    if request.method == "POST":
        # ensure username, semi redundant with require but checking for safety
        error = None
        
        username = request.form.get("username")
        if not username:
            return apology("must provide username")
        if not fullmatch(USERNAME_RE, username):
            return apology("invalid username (allowed: letters, digits, _, -; 3-30 chars)")

        existing = query_db("SELECT id FROM users WHERE username = ?", (username,), one=True)
        if existing: 
            return apology("username already taken")

        password = request.form.get("password")
        if not password:
            return apology("must provide password")

        pconfirm = request.form.get("confirmation")
        if not pconfirm:
            return apology("must confirm password")

        password = fullmatch(PASSREG, password)
        if not password:
            return apology("invalid password")
        password = password.group()

        if password != pconfirm:
            return apology("passwords not identical")
        
        try:
            execute_db("INSERT INTO users(username, password_hash) VALUES (?, ?)",
                   (username, generate_password_hash(password)))
            user_folder = os.path.join(current_app.config["UPLOAD_FOLDER"], username)
            os.makedirs(user_folder, exist_ok=True)
        except sqlite3.IntegrityError:
            flash(f"User {username} is already registered", "danger")
            return render_template('register.html')
        except Exception as e:
            flash("Error registering user")
            return apology("Database error, please try again later")
        else:
            return redirect(url_for("auth.login"))
        

    if request.method == "GET":
        return render_template("register.html")


@bp.route("/account", methods=["GET", "POST"])
@login_required
def account():
    if request.method == "POST":
        old = request.form.get("old")
        if not old:
            return apology("Old password not entered")
        
        password_check = query_db(
            "SELECT password_hash FROM users WHERE username = ?", (session['username'],))
        
        if not check_password_hash(password_check[0]['password_hash'], old):
            return apology("Old password incorrect")
        
        new = request.form.get("new")
        if not new:
            return apology("New password not entered")
        confirm = request.form.get("confirm")
        if not confirm:
            return apology("Confirm password not entered")

        new = fullmatch(PASSREG, new)
        if not new:
            return apology("invalid password")
        new = new.group()

        if not new == confirm:
            return apology("Not the same")

        try:
            execute_db("UPDATE users SET password_hash = ? WHERE id = ?",
                       (generate_password_hash(new), session["user_id"]))
        except:
            return apology("Database error, try again later!")

        return redirect("/")

    if request.method == "GET":
        user = query_db("SELECT username FROM users WHERE id = ?",
                          (session["user_id"],))[0]["username"]
        return render_template("account.html", user=user)

    
@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
            'SELECT * FROM users WHERE id = ?', (user_id,)
        ).fetchone()



