import pytest
from dbbv.utils.query_history import MAX_HISTORY_ITEMS


def test_index(client, auth):
    response = client.get("/", follow_redirects=True)
    assert b"Please sign in" in response.data
    assert b"Register" in response.data

    auth.login()
    response = client.get("/")
    assert b"Log Out" in response.data
    assert b"Account" in response.data
    assert b"File Upload" in response.data
    assert b"SQLite" in response.data

    response = client.post(
        "/",
        data={"action": "run", "query": "SELECT * FROM sqlite_master"},
        follow_redirects=True,
    )

    assert b"No database selected" in response.data


def test_sqlite_routes(client, auth):
    auth.login()

    with open("tests/sql_tests.sql") as f:
        script = f.read()

    client.get("/")
    with client.session_transaction() as sess:
        sess["db_selected"] = "example.db"

    # test clearing db
    clearing = client.post("/", data={"action": "clear"}, follow_redirects=True)
    assert b"Run a query to see the result here!" in clearing.data

    # test get_remove
    client.post("/", data={"action": "run", "query": "SELECT * FROM projects;"})
    removing = client.post("/", data={"remove": 0})
    assert removing.status_code == 200
    assert removing.is_json
    assert removing.get_json()["empty"] is True

    client.post("/", data={"action": "run", "query": "SELECT * FROM projects;"})
    client.post("/", data={"action": "run", "query": "SELECT * FROM projects;"})
    removing = client.post("/", data={"remove": 0})
    assert removing.status_code == 200
    assert removing.is_json
    assert removing.get_json()["empty"] is False

    removing = client.post("/", data={"remove": "abc"})
    assert removing.status_code == 400
    assert removing.is_json
    assert removing.get_json()["error"] == "Invalid index"

    removing = client.post("/", data={"remove": -1})
    assert removing.status_code == 400
    assert removing.is_json
    assert removing.get_json()["error"] == "Index out of bounds"

    # test querying
    response = client.post(
        "/", data={"action": "run", "query": script}, follow_redirects=True
    )
    assert response.status_code == 200
    assert b"PRAGMA index_list (&#39;orders&#39;);" in response.data


@pytest.mark.parametrize(
    ("query", "result"),
    (
        (
            # testing incomplete statement
            """SELECT id, name
            FROM projects
            WHERE status = 'active """,
            b"Incomplete statement(s)",
        ),
        (
            # testing empty or comment only statement
            "-- this line is just a comment",
            "",
        ),
        (
            # testing DB error
            "SELECT * FROM missing_table;",
            b"no such table",
        ),
        (
            # testing DB error for empty list return
            "SELECT * FROM projects WHERE id = -9999;",
            b"Query returned no rows",
        ),
        (
            # testing DB error MAX_RESULT_ROWS
            """-- Seed a quick test table with 150 rows
                        CREATE TABLE IF NOT EXISTS spam (id INTEGER PRIMARY KEY, note TEXT);
                        WITH RECURSIVE seq(x) AS (
                        SELECT 1
                        UNION ALL
                        SELECT x + 1 FROM seq WHERE x < 150
                        )
                        INSERT INTO spam(note)
                        SELECT 'row ' || x
                        FROM seq;

                        -- Query exceeding the limit
                        SELECT * FROM spam;""",
            b"MAX_RESULT_ROWS exceeded",
        ),
    ),
)
def test_run_queries(client, auth, query, result):
    auth.login()

    client.get("/")
    with client.session_transaction() as sess:
        sess["db_selected"] = "example.db"

    response = client.post(
        "/",
        data={"action": "run", "query": query},
        follow_redirects=True,
    )
    assert response.status_code == 200
    if result != "":
        assert result in response.data


def test_max_items(client, auth):
    auth.login()
    client.get("/")

    with client.session_transaction() as sess:
        sess["db_selected"] = "example.db"

    for i in range(MAX_HISTORY_ITEMS + 1):
        response = client.post(
            "/",
            data={"action": "run", "query": "SELECT * FROM sqlite_master;"},
            follow_redirects=True,
        )

    assert response.status_code == 200
    assert b"MAX_HISTORY_ITEMS exceeded" in response.data
