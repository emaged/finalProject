import os
import sqlite3
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, current_app
)
from werkzeug.security import check_password_hash, generate_password_hash
from re import fullmatch
from dbbv.db import get_db, query_db, execute_db
from dbbv.routes.helpers import login_required
    
USERNAME_RE = r'^[A-Za-z0-9_-]{3,30}$'
PASSREG = r'''^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$'''


bp = Blueprint('auth', __name__)

@bp.route('/login', methods=['GET', 'POST'])
def login():
    '''Log user in'''

    # User reached route via POST (as by submitting a form via POST)
    if request.method == 'POST':
        # Ensure username was submitted
        if not request.form.get('username'):
            flash('must provide username', 'danger')
            return redirect(request.url)

        # Ensure password was submitted
        elif not request.form.get('password'):
            flash('must provide password', 'danger')
            return redirect(request.url)

        # Query database for username
        rows = query_db(
            'SELECT * FROM users WHERE username = ?', (request.form.get('username'),)
        )

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0]['password_hash'], request.form.get('password')
        ):
            flash('invalid username and/or password', 'danger')
            print('hi there')
            return render_template('login.html')

        # Forget any user_id
        session.clear()

        # Remember which user has logged in
        session['user_id'] = rows[0]['id']
        session['username'] = rows[0]['username']
        user_folder = os.path.join(current_app.config['UPLOAD_FOLDER'], rows[0]['username'])
        session['user_folder'] = user_folder 
        os.makedirs(user_folder, exist_ok=True)
        session['db_selected'] = None
        session['paired_queries'] = []
        session['schemas'] = []
        # Redirect user to home page
        if request.form.get('remember'):
            session.permanent = True 
        else:
            session.permanent = False
        
        return redirect(url_for('sqlite.index'))

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template('login.html')
    
@bp.route('/logout')
def logout():
    '''Log user out'''

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect(url_for('sqlite.index'))

@bp.route('/register', methods=['GET', 'POST'])
def register():
    '''Register user'''

    # User reached via Post
    if request.method == 'POST':
        # ensure username, semi redundant with require but checking for safety
        error = None
        
        username = request.form.get('username')
        if not username:
            flash('must provide username', 'danger')
            return redirect(request.url)
        if not fullmatch(USERNAME_RE, username):
            flash('invalid username (allowed: letters, digits, _, -; 3-30 chars)', 'danger')
            return redirect(request.url)

        existing = query_db('SELECT id FROM users WHERE username = ?', (username,), one=True)
        if existing: 
            flash('username already taken', 'danger')
            return redirect(request.url)

        password = request.form.get('password')
        if not password:
            flash('must provide password', 'danger')
            return redirect(request.url)

        pconfirm = request.form.get('confirmation')
        if not pconfirm:
            flash('must confirm password', 'danger')
            return redirect(request.url)

        password = fullmatch(PASSREG, password)
        if not password:
            flash('invalid password', 'danger')
            return redirect(request.url)
        password = password.group()

        if password != pconfirm:
            flash('passwords not identical', 'danger')
            return redirect(request.url)
        
        try:
            execute_db('INSERT INTO users(username, password_hash) VALUES (?, ?)',
                   (username, generate_password_hash(password)))
            user_folder = os.path.join(current_app.config['UPLOAD_FOLDER'], username)
            os.makedirs(user_folder, exist_ok=True)
        except sqlite3.IntegrityError:
            flash(f'User {username} is already registered', 'danger', 'danger')
            return render_template('register.html')
        except Exception as e:
            flash('Error registering user', 'danger')
            return redirect(request.url) 
        else:
            return redirect(url_for('auth.login'))
        

    if request.method == 'GET':
        return render_template('register.html')


@bp.route('/account', methods=['GET', 'POST'])
@login_required
def account():
    if request.method == 'POST':
        old = request.form.get('old')
        if not old:
            flash('Old password not entered', 'danger')
            return redirect(request.url)
        
        password_check = query_db(
            'SELECT password_hash FROM users WHERE username = ?', (session['username'],))
        
        if not check_password_hash(password_check[0]['password_hash'], old):
            flash('Old password incorrect', 'danger')
            return redirect(request.url)
        
        new = request.form.get('new')
        if not new:
            flash('New password not entered', 'danger')
            return redirect(request.url)
        confirm = request.form.get('confirm')
        if not confirm:
            flash('Confirm password not entered', 'danger')
            return redirect(request.url)

        new = fullmatch(PASSREG, new)
        if not new:
            flash('invalid password', 'danger')
            return redirect(request.url)
        new = new.group()

        if not new == confirm:
            flash('Not the same', 'danger')
            return redirect(request.url)

        try:
            execute_db('UPDATE users SET password_hash = ? WHERE id = ?',
                       (generate_password_hash(new), session['user_id']))
        except:
            flash('Database error, try again later!', 'danger')
            return redirect(request.url)

        return redirect('/')

    if request.method == 'GET':
        user = query_db('SELECT username FROM users WHERE id = ?',
                          (session['user_id'],))[0]['username']
        return render_template('account.html', user=user)

    
@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
            'SELECT * FROM users WHERE id = ?', (user_id,)
        ).fetchone()



