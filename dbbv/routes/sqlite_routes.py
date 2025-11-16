from flask import(
    Blueprint, flash, redirect, render_template, request, session, url_for, current_app
)
from dbbv.utils.helpers import login_required, check_user_folder, list_user_files
from dbbv.user_db.user_sqlite import query_db_sqlite, combined_exec_db_sqlite, format_query_result
from dbbv.utils.query_history import load_history, save_history

bp = Blueprint('sqlite', __name__)


@bp.route('/', methods=['GET', 'POST'])
@login_required
def index():
    user_folder = check_user_folder()
    files = list_user_files() 
    paired_queries = load_history(user_folder)
    
    if session.get('db_selected'):
        schemas = query_db_sqlite('SELECT * FROM sqlite_master')
    else:
        schemas = None
    
    if request.method == 'POST':
        # Run the query
        if request.form.get('action') == 'run' and request.form.get('query'):
            if not session.get('db_selected'):
                flash('No database selected')
                return redirect(url_for('sqlite.index'))
            query = request.form.get('query')
            try:
                query_result = combined_exec_db_sqlite(query, commit=True)
                header, formatted_result = format_query_result(query_result)
            except Exception as e:
                flash(e)
                return redirect(url_for('sqlite.index'))
            
            paired_queries = [[query, header, formatted_result]] + paired_queries
            save_history(user_folder, paired_queries)
        
        # Clear queries
        elif request.form.get('action') == 'clear':
            paired_queries = []
            save_history(user_folder, paired_queries)

        elif request.form.get('remove'):
            popIndex = int(request.form.get('remove'))
            paired_queries = load_history(user_folder)
            paired_queries.pop(popIndex)
            save_history(user_folder, paired_queries)
            
            # return goes to js
            if not paired_queries:
                return '1'
            else:
                return '0'

    # replace with session.get in production code for safety 
    return render_template('index.html', files=files, db_selected=session['db_selected'],
                           paired_queries=paired_queries, schemas=schemas) 
