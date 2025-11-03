import os
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, current_app
)
from werkzeug.security import check_password_hash, generate_password_hash
from re import fullmatch
from dbbv.db import get_db, query_db, execute_db
from dbbv.routes.helpers import apology, passreg, login_required

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
        session["user_folder"] = os.path.join(current_app.config["UPLOAD_FOLDER"], rows[0]["username"])
        print(session["user_folder"])
        os.makedirs(session["user_folder"], exist_ok=True)
        # Redirect user to home page
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

        users = query_db("SELECT username FROM users")
        for u in users:
            if username == u["username"]:
                return apology("username already taken")

        password = request.form.get("password")
        if not password:
            return apology("must provide password")

        pconfirm = request.form.get("confirmation")
        if not pconfirm:
            return apology("must confirm password")

        password = fullmatch(passreg, password)
        if not password:
            return apology("invalid password")
        password = password.group()

        if password != pconfirm:
            return apology("passwords not identical")
        
        try:
            execute_db("INSERT INTO users(username, password_hash) VALUES (?, ?)",
                   (username, generate_password_hash(password)))
        except get_db().IntegrityError:
            error = f"User {username} is already registered"
        else:
            return redirect(url_for("auth.login"))
        
        print(error)
        flash(error, "danger")

        return render_template('register.html')

    if request.method == "GET":
        return render_template("register.html")


@bp.route("/account", methods=["GET", "POST"])
def account():
    if request.method == "POST":
        old = request.form.get("old")
        if not old:
            return apology("Old password not entered")
        new = request.form.get("new")
        if not new:
            return apology("New password not entered")
        confirm = request.form.get("confirm")
        if not confirm:
            return apology("Confirm password not entered")

        new = fullmatch(passreg, new)
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
        print("No User Logged in")
    else:
        g.user = get_db().execute(
            'SELECT * FROM users WHERE id = ?', (user_id,)
        ).fetchone()
        print(f"Logged in user: {g.user['username']}")



