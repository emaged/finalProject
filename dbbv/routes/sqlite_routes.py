from flask import (
    Blueprint,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from dbbv.utils.helpers import login_required, check_user_folder, list_user_files
from dbbv.user_db.user_sqlite import (
    query_db_sqlite,
    combined_exec_db_sqlite,
    format_query_result,
)
from dbbv.utils.query_history import (
    load_history,
    save_history,
    MAX_HISTORY_ITEMS,
    MAX_RESULT_ROWS,
)

bp = Blueprint("sqlite", __name__)


@bp.route("/", methods=["GET", "POST"])
@login_required
def index():
    user_folder = check_user_folder()
    files = list_user_files()
    paired_queries = load_history(user_folder)

    db_selected = session.get("db_selected")
    if db_selected:
        schemas = query_db_sqlite("SELECT * FROM sqlite_master")
    else:
        schemas = None

    action = request.form.get("action")
    query = request.form.get("query")
    get_remove = request.form.get("remove")

    if request.method == "POST":
        # Run the query
        if action == "run" and query:
            if not db_selected:
                flash("No database selected", "dark")
                return redirect(url_for("sqlite.index"))
            try:
                query_result = combined_exec_db_sqlite(query, commit=True)
                header, formatted_result = format_query_result(query_result)
            except Exception as e:
                flash(e, "danger")
                return redirect(url_for("sqlite.index"))

            if len(formatted_result) > MAX_RESULT_ROWS:
                flash("MAX_RESULT_ROWS exceeded, truncated rows 100+", "warning")
                rows = formatted_result[:MAX_RESULT_ROWS]
            else:
                rows = formatted_result

            paired_queries.insert(0, [query, header, rows])

            if len(paired_queries) > MAX_HISTORY_ITEMS:
                flash(
                    "MAX_HISTORY_ITEMS exceeded, deleted the last query from your history",
                    "warning",
                )
            paired_queries = save_history(user_folder, paired_queries)

        # Clear queries
        elif action == "clear":
            paired_queries = []
            save_history(user_folder, paired_queries)

        elif get_remove:
            popIndex = int(get_remove)
            paired_queries.pop(popIndex)
            save_history(user_folder, paired_queries)

            # return goes to js
            if not paired_queries:
                return "1"
            else:
                return "0"

    # replace with session.get in production code for safety
    return render_template(
        "index.html",
        files=files,
        db_selected=db_selected,
        paired_queries=paired_queries,
        schemas=schemas,
    )
