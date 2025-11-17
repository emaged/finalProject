
# DataBase Browser Viewer
Web app to inspect and change simple sqlite database files.

## Description

## Video Demo
(Add a screenshot or GIF here showing the app in action.)

## Tech stack
- Python 3.12+ 
- Framework: Flask, Bootstrap
- Database: SQLite 
- Frontend: HTML/CSS/JS 

## Features
-
- 
- 
- 
- 

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

```bash
pip install -r requirements.txt
```
Or install the development suite
```bash
pip install -r requirements-dev.txt
```

## Environment
- To set and control environment variables, create a `.env` file in the project directory. For example:
```bash
FLASK_APP=dbbv # sets FLASK_APP for executing flask run
FLASK_DEBUG=1  # sets FLASK_DEBUG to enable debugging. disable for production
```

Run locally
```bash
# example - update for your project
poetry run python -m app         # or `flask run` / `python run.py`
```

Run tests
```bash
poetry run pytest
```

Lint & format
```bash
poetry run ruff check .
poetry run black .
```

## Project structure
- dbbv/ — application code
- dbbv/templates/ — HTML templates
- dbbv/static/ — CSS, JS, images
- dbbv/user_db — 
- dbbv/utils — utility functions
- tests/ — automated tests

## Contribution
Please see CONTRIBUTING.md for guidelines on contributing.

## License
This project is licensed under the MIT License — see LICENSE.md.


Web app to inspect and change simple sqlite database files

Don't forget to add a secret key to the /instance/config.py file!

for setting the .env file:
FLASK_APP=dbbv
if you want debugging enabled
FLASK_DEBUG=1

to set up the main database run:
    flask --app dbbv init-db 
to generate a secret key run: 
    python -c 'import secrets; print(secrets.token_hex())'

save this key to your /instance/config.py file:
SECRET_KEY = 'your_generated_secret_key'

MAX_HISTORY_SIZE is set at 30 for number of queries in memory