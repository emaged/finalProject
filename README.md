# DataBase Browser Viewer

Web app to inspect and change simple sqlite database files.

## Description

The idea for this application came to me when working on the CS50 Fiftyville problem. I was writing SQL queries in the terminal and copying the results to an external editor, and this seemed like an impractical way to view database queries. So I decided to make a modern web application to easily write queries to any SQLite database and view their results in an organized, neatly displayed way.

In this short introduction, I will quickly go through the functionality of the web app. To set up and run the application, please read the instructions provided below.

First, a user has to create an account. This creates a personal folder where they can upload their database files, ensuring each user only has access to their own data.

After logging in, the user will be presented with a main page, where they can run and clear their queries, select which database to run queries on, and view the database schemas. The queries are displayed in Bootstrap tables, and can be deleted individually or cleared as a group.

On the File Upload page, the user can choose to upload an SQLite database (only SQLite databases will work, with the `.db`, `.sqlite`, or `.sqlite3` extension), or to create a new database with a given filename.

The Account page provides an option for the user to change their password.

## Video Demo

(Add a screenshot or GIF here showing the app in action.)

## Tech stack

- Python 3.12+
- Framework: Flask, Bootstrap
- Database: SQLite
- Frontend: HTML/CSS/JS

## Features

- Upload and/or create sqlite databases
- Run queries to alter/view databases
- Easy swapping between multiple databases
- Modern Bootstrap UI
- View DB schemas for convenient overview of DB structure
- Per user DB acces, allowing for safely uploading personal databases
- Simple account management, just register/login/logout and change password

## Getting started

Prerequisites

- Python 3.12+
- Poetry (or pip + venv)

Clone the git repo into your directory:

```bash
git clone https://github.com/emaged/finalProject.git
```

Install dependencies with poetry:

```bash
poetry install
```

Alternatively, Install dependencies with pip.

First set up a virtual environment with venv\
When using linux:

```bash
python -m venv .venv
source .venv/bin/activate
```

Or on windows using cmd:

```cmd
python -m venv .venv
.venv\scripts\activate.bat
```

Ensure pip is installed:

```bash
python -m ensurepip --upgrade
```

Then install the requirements.txt:

```bash
pip install -r requirements.txt
```

Or install the development suite

```bash
pip install -r requirements-dev.txt
```

### Installing wheel file

It's also possible to directly install the project using pip.

Either build a `.whl` file; from the directory containing pyproject.toml run:

```bash
poetry build
```

Or

```bash
python3 -m pip install --upgrade build
python3 -m build
```

#### Remember to activate your venv before installing

Locate the `.whl` file (usually under `/dist`) and run:

```bash
pip install "PATH_TO_YOUR_WHEEL_FILE"
```

Or install directly from TestPyPI:

```bash
pip install -i https://test.pypi.org/simple/ DBBV
```

## Environment

To set up the main database run:

```bash
flask --app dbbv init-db
```

To set and control environment variables, create a `.env` file in the project directory. For example:

```python
FLASK_APP=dbbv # sets FLASK_APP for executing flask run
FLASK_DEBUG=1  # sets FLASK_DEBUG to enable debugging. disable for production
```

Setting `FLASK_APP` (and `FLASK_DEBUG` when debugging) is recommended for easier CLI commands

### Don't forget to add a secret key to the /instance/config.py file

To generate a secret key run:

```bash
python -c 'import secrets; print(secrets.token_hex())'
```

Save this key to your /instance/config.py file:

```python
SECRET_KEY = 'your_generated_secret_key'
```

`MAX_HISTORY_SIZE` is set at 30 for number of queries in memory\
`MAX_RESULTS_ROWS` is set at 100 for number of rows in query result\
These settings can be changed in `query_history.py`

```python
MAX_HISTORY_ITEMS = 30
MAX_RESULT_ROWS = 100
```

## Running the application

To run with flask's test server, make sure your venv is activated and run:

```bash
flask run
```

If you haven't set `FLASK_APP` and `FLASK_DEBUG` use:

```bash
flask --app dbbv run --debug
```

### Run with a production server

When running publicly instead of in development, you shouldn't use the built in server `flask run`. Instead, use a production WSGI server.
For example, to use Waitress (installed as dependency):

```bash
waitress-serve --call 'dbbv:create_app'
```

You should see something like `INFO:waitress:Serving on http://0.0.0.0:8080`

Run tests with pytest from the project root:

```bash
pytest
```

Coverage is included in the dependencies. To use it run:

```bash
coverage run -m pytest
coverage report
coverage html # for a more detailed report
```

## Project structure

- dbbv/ — application code
- dbbv/templates/ — HTML templates
- dbbv/static/ — CSS, JS, images
- dbbv/user_db — functions interacting with the user databases
- dbbv/utils — utility functions
- tests/ — automated tests

A short overview of the most important files:

### dbbv/

`__init__.py` \
Flask app factory; sets defaults, loads config, ensures instance/session dirs, wires CSRF, server-side session cache, core database, and blueprints.

`db.py`\
Core SQLite helper; opens the main app DB with foreign keys, registers teardown/CLI init, and exposes query_db/execute_db helpers.

`schema.sql`\
Schema for the built-in user database (users + user_dbs tables with FK enforcement).

### dbbv/routes/

`auth.py`\
Authentication/account blueprint. Handles register/login/logout, password validation, password change flow, and loading g.user on every request.

`files.py`\ File-management blueprint. Uploads validated SQLite files, lists them, handles download/delete/create, and updates the selected DB in session via AJAX.

`sqlite_routes.py`\ Main query UI. Shows history, schemas, executes arbitrary SQL against the user-selected database, enforces history/result limits, and persists history per user.

`__init__.py`\
Empty placeholder to mark the package.

### dbbv/static/

`css/sidebar.css`\
Styles the sidebar collapsible list and schema tables.

`css/sign-in.css`\
Bootstrap overrides for the login/register forms.

`js/sidebar.js`\
Client logic for selecting DB files, refreshing schemas, and wiring the delete-file modal (wrapped in DOMContentLoaded with CSRF header handling).

`js/queries.js`\
Handles removing stored query cards via AJAX, keeping indices in sync, and showing a message when all history is cleared.

`img/…`\
Logo and favicon assets.

### dbbv/templates/

`layout.html`\
Base template providing nav, auth-aware layout, flash messaging, modals, scripts, and CSRF meta tag.

`index.html`\
Query console UI; shows editable query form, history cards, and the clear-history modal.

`files.html`\
Upload/create databases form plus sidebar layout.

`account.html`\
Password change form with requirements list.

`login.html`\
Standalone login page with remember-me and password toggle.

`register.html`\
Registration page (extends layout) with validation hints.

`sidebar.html`\
Shared sidebar listing user DB files and dynamic schema tables.

### dbbv/user_db/

`user_sqlite.py`\
Manages per-user database connections (with caching in g), foreign key PRAGMA, executes queries/mutations, and formats results for display.

### dbbv/utils/

`helpers.py`\
Misc helpers (auth decorator, upload filters, path helpers, CSRF-safe user folder setup).

`query_history.py`\
Reads/writes per-user query_history.json with configurable limits on stored queries/results.

## Project layout

```bash
├── dbbv
│   ├── __init__.py
│   ├── __pycache__
│   ├── db.py
│   ├── routes
│   │   ├── __init__.py
│   │   ├── __pycache__
│   │   ├── auth.py
│   │   ├── files.py
│   │   └── sqlite_routes.py
│   ├── schema.sql
│   ├── static
│   │   ├── css
│   │   │   ├── sidebar.css
│   │   │   └── sign-in.css
│   │   ├── img
│   │   │   ├── favicon1.ico
│   │   │   └── logo_final.png
│   │   └── js
│   │       ├── queries.js
│   │       └── sidebar.js
│   ├── templates
│   │   ├── account.html
│   │   ├── files.html
│   │   ├── index.html
│   │   ├── layout.html
│   │   ├── login.html
│   │   ├── register.html
│   │   └── sidebar.html
│   ├── user_db
│   │   ├── __init__.py
│   │   ├── __pycache__
│   │   └── user_sqlite.py
│   └── utils
│       ├── __init__.py
│       ├── __pycache__
│       ├── helpers.py
│       └── query_history.py
├── eslint.config.js
├── flask_session
├── instance
│   ├── config.py
│   ├── dbbv.sqlite
│   ├── session_cache
│   ├── test_user_databases
│   └── user_databases
├── LICENSE.md
├── package-lock.json
├── package.json
├── poetry.lock
├── pyproject.toml
├── README.md
├── requirements-dev.txt
├── requirements.txt
└── tests
    ├── __init__.py
    ├── __pycache__
    ├── conftest.py
    ├── data.sql
    ├── test_auth.py
    ├── test_db.py
    ├── test_factory.py
    ├── test_files.py
    └── test_sqlite.py
```

## License

This project is licensed under the MIT License — see LICENSE.md.
