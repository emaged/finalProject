# DataBase Browser Viewer

Web app to inspect and change simple sqlite database files.

## Description

The idea for this application came to me when working on the CS50 fiftyville problem. I was writing SQL queries in the terminal and copying the text to an external editor, and this seemed like an unpractical way to view database queries. So i decided to make a modern web application to easily write queries to any SQLite database and view their results in an ordered and neatly displayed way.

In this short introduction I will quickly go through the functionality of the web app. To set up and run the application, please read the instructions provided below.

First, a user has to create an account. This creates a folder for this user where he can upload his database files to. In this way, every user only has acces to his own database files.

After logging in, the user will be presented with a main page, where he can run and clear his queries, select which database to run queries on, and view the database schemas. The queries are displayed in nice Bootstrap tables, and can be either individually deleted, or be deleted as a group.

On the File Upload page, the user can choose to upload a SQLite database (Only SQLite databases will work, with the .db, .sqlite or .sqlite3 extension), or choose to create a new database with a given filename.

The Account page gives an option to change your password.

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
- View DB schemas for convenient overview of db structure
- Per user db acces, allowing for safely uploading personal databases
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

## Environment

- to set up the main database run:

```bash
flask --app dbbv init-db
```

- To set and control environment variables, create a `.env` file in the project directory. For example:

```python
FLASK_APP=dbbv # sets FLASK_APP for executing flask run
FLASK_DEBUG=1  # sets FLASK_DEBUG to enable debugging. disable for production
```

setting `FLASK_APP` (and `FLASK_DEBUG` when debugging) is recommended for easier CLI commands

### Don't forget to add a secret key to the /instance/config.py file

To generate a secret key run:

```bash
python -c 'import secrets; print(secrets.token_hex())'
```

save this key to your /instance/config.py file:

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

To run with flasks test server, make sure your venv is activated and run:

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

you should see something like `INFO:waitress:Serving on http://0.0.0.0:8080`

Run tests with pytest from the project root:

```bash
pytest
```

## Project structure

- dbbv/ — application code
- dbbv/templates/ — HTML templates
- dbbv/static/ — CSS, JS, images
- dbbv/user_db — functions interacting with the user databases
- dbbv/utils — utility functions
- tests/ — automated tests

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
