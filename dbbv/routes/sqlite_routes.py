from flask import (
    Blueprint,
    current_app,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from sqlparse import split, format
from sqlite3 import complete_statement
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
    action = request.form.get("action")
    query = request.form.get("query")
    get_remove = request.form.get("remove")

    if request.method == "POST":
        # Run the query
        if action == "run" and query:
            if not db_selected:
                flash("No database selected", "dark")
                return redirect(url_for("sqlite.index"))

            # support for multiline statements
            statements = []
            for raw in split(query):
                cleaned = format(raw, strip_comments=True).strip()
                if not cleaned:
                    continue
                if not complete_statement(cleaned):
                    flash("Incomplete statement(s) in your query", "warning")
                    return redirect(url_for("sqlite.index"))
                statements.append(cleaned)

            for statement in statements:
                try:
                    query_result = combined_exec_db_sqlite(statement, commit=True)
                    header, formatted_result = format_query_result(query_result)
                except Exception as e:
                    flash(e, "danger")
                    return redirect(url_for("sqlite.index"))

                if formatted_result is None:
                    # meaning exactly None
                    rows = [{"status": "Query executed successfully"}]
                elif not formatted_result:
                    # meaning empty list
                    rows = [{"status": "Query returned no rows"}]
                elif len(formatted_result) > MAX_RESULT_ROWS:
                    flash("MAX_RESULT_ROWS exceeded, truncated rows 100+", "warning")
                    rows = formatted_result[:MAX_RESULT_ROWS]
                else:
                    rows = formatted_result

                paired_queries.insert(0, [statement, header, rows])

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
            # returns goes to js
            try:
                popIndex = int(get_remove)
            except (ValueError, TypeError):
                current_app.logger.error(f"Invalid index received: {get_remove}")
                return jsonify({"error": "Invalid index"}), 400

            if popIndex >= len(paired_queries) or popIndex < 0 or not paired_queries:
                current_app.logger.error("Out of bounds error from popIndex")
                return jsonify({"error": "Index out of bounds"}), 400

            paired_queries.pop(popIndex)
            save_history(user_folder, paired_queries)

            # tell the client whether the list is now empty
            return jsonify({"empty": not paired_queries}), 200

    # defer loading schemas until after POST
    if db_selected:
        schemas = query_db_sqlite("SELECT * FROM sqlite_master")
    else:
        schemas = None

    return render_template(
        "index.html",
        files=files,
        db_selected=db_selected,
        paired_queries=paired_queries,
        schemas=schemas,
    )


@bp.before_app_request
def log_request_marker():
    current_app.logger.info("\n")
    current_app.logger.info("--- %s %s ---", request.method, request.path)
