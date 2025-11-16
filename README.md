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