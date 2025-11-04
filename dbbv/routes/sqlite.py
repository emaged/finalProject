from os import listdir
from os.path import isfile, join
from flask import(
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
    
from dbbv.db import get_db, query_db, execute_db
from dbbv.routes.helpers import apology, login_required

bp = Blueprint('sqlite', __name__)

@bp.route("/", methods=['GET', 'POST'])
@login_required
def index():
    files = [file for file in listdir(session["user_folder"]) if isfile(join(session["user_folder"], file))]
    if request.method == 'POST':
        # Run the query
        if request.form.get("action") == "run":
           print("running") 
        
        # Clear queries
        elif request.form.get("action") == "clear":
            print("clearing")
            pass
        
    if request.method == 'GET':
        pass
    return render_template("index.html", files=files, db_selected=session["db_selected"]) 