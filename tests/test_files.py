import io
import sqlite3
import os
import tempfile
from dbbv.user_db.user_sqlite import query_db_sqlite
from flask import session

# beware test files are created and used by multiple functions
# cleanup is not per function


def create_sqlite_file():
    fd, tmp_path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    conn = sqlite3.connect(tmp_path)
    # WARNING does not delete old table t if it exists in the user folder
    conn.execute("DROP TABLE IF EXISTS t")
    conn.execute("CREATE TABLE IF NOT EXISTS t (id INTEGER PRIMARY KEY, descr TEXT)")
    conn.execute("INSERT INTO t(descr) VALUES ('first')")
    conn.execute("INSERT INTO t(descr) VALUES ('second')")
    conn.execute("INSERT INTO t(descr) VALUES ('third')")
    conn.commit()
    conn.close()

    with open(tmp_path, "rb") as f:
        bio = io.BytesIO(f.read())

    os.remove(tmp_path)
    return bio


def create_test_db(client, name="example2.db"):
    with client:
        client.get("/")
        user_folder = session["user_folder"]

        os.makedirs(user_folder, exist_ok=True)
        path = os.path.join(user_folder, name)
        sqlite3.connect(path).close()


def test_upload(client, auth):
    auth.login()

    with client:
        client.get("/")
        user_folder = session["user_folder"]

    data = {"file": (create_sqlite_file(), "example.db")}
    response = client.post(
        "/upload", data=data, content_type="multipart/form-data", follow_redirects=True
    )
    assert response.status_code == 200
    assert b"This is the files page." in response.data

    path = os.path.join(user_folder, "example.db")
    assert os.path.exists(path)


def test_download(client, auth):
    auth.login()

    response = client.get("/download/example.db")

    assert response.status_code == 200
    assert response.data.startswith(b"SQLite format 3")

    response2 = client.get("/download/not_exists.db", follow_redirects=True)
    assert response2.status_code == 200
    assert b"File not found" in response2.data


def test_select(client, auth, app):
    auth.login()

    # create_test_db(client)

    response = client.post("/select", data={"selected_file": "example.db"})
    assert response.status_code == 200
    assert response.is_json
    response_data = response.get_json()
    assert isinstance(response_data, list)

    with client:
        client.get("/")
        expected_data = query_db_sqlite("SELECT * FROM sqlite_master")

    # Compare names only
    response_names = {row["name"] for row in response_data}
    expected_names = {row["name"] for row in expected_data}
    assert response_names == expected_names


def test_removeFile(client, auth):
    auth.login()
    with client:
        client.get("/")
        user_folder = session["user_folder"]

    create_test_db(client, "example2.db")

    filePath = os.path.join(user_folder, "example2.db")
    assert os.path.exists(filePath)

    response = client.post(
        "/remove", data={"remove": "example2.db"}, follow_redirects=True
    )

    assert response.status_code == 200
    assert not os.path.exists(filePath)

    response2 = client.post(
        "/remove", data={"remove": "example2.db"}, follow_redirects=True
    )

    assert response2.status_code == 200
    assert b"The file does not exist" in response2.data


def test_create(client, auth):
    auth.login()
    with client:
        client.get("/")
        user_folder = session["user_folder"]

    response = client.post(
        "/create",
        data={"filename": "newtest", "extension": "db"},
        follow_redirects=True,
    )
    assert response.status_code == 200

    full_path = os.path.join(user_folder, "newtest.db")
    assert os.path.exists(full_path)
    os.remove(full_path)
    assert not os.path.exists(full_path)
