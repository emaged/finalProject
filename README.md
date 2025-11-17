# finalProject
DataBase Browser Viewer

## Description
Web app to inspect and change simple sqlite database files

## Video Demo
(Add a screenshot or GIF here showing the app in action.)

## Tech stack
- Python 3.12+ 
- Framework: Flask 3.03+, Bootstrap
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

Install dependencies
```bash
poetry install
```

Environment
- Copy `.env.example` to `.env` and fill in required environment variables.

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