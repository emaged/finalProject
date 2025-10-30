import os
from re import fullmatch
from flask import Flask, redirect, render_template, request, session
from flask_session import Session
from flask_login import login_user, logout_user, current_user, login_required  
from werkzeug.security import check_password_hash, generate_password_hash

from dbbv.routes.helpers import apology, passreg

UPLOAD_FOLDER = '/user_databases'
ALLOWED_EXTENSIONS = ('db')

app = Flask(__name__)

# app.config['SESSION_PERMANENT'] = False
# app.config['SESSION_TYPE'] = 'filesystem'
# app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# app.config['MAX_CONTENT_LENGTH'] = 16 * 1000 * 1000
#
Session(app)

@app.route('/')
def index():
    return "hello world"

@app.route("/login", methods=["GET", "POST"])
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
        rows = db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get("username")
        )

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0]["hash"], request.form.get("password")
        ):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")
    
@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    # User reached via Post
    if request.method == "POST":
        # ensure username, semi redundant with require but checking for safety
        username = request.form.get("username")
        if not username:
            return apology("must provide username")

        users = db.execute("SELECT username FROM users")
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
            return apology("invalid pasword")
        password = password.group()

        if password != pconfirm:
            return apology("passwords not identical")

        db.execute("INSERT INTO users(username, hash) VALUES (?, ?)",
                   username, generate_password_hash(password))

        return redirect("/login")

    if request.method == "GET":
        return render_template("register.html")