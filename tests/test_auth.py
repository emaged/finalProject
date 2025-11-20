import pytest
from flask import g, session


def test_register(client, app):
    assert client.get("/register").status_code == 200
    response = client.post(
        "/register",
        data={"username": "mary", "password": "Hello123!", "confirmation": "Hello123!"},
    )
    assert response.status_code == 302
    assert response.headers["Location"] == "/login"


@pytest.mark.parametrize(
    ("username", "password", "confirmation", "message"),
    (
        ("", "", "", b"must provide username"),
        ("abc", "", "", b"must provide password"),
        ("test", "Testpas123!", "Testpas123", b""),
        ("test", "Testpas123!", "Testpas123", b"username already taken"),
    ),
)
def test_register_validate_input(client, username, password, confirmation, message):
    response = client.post(
        "/register",
        data={"username": username, "password": password, "confirmation": confirmation},
        follow_redirects=True,
    )
    try:
        assert message in response.data
    except AssertionError:
        # print(response.data.decode())
        raise


### second snippet ###
def test_login(client, auth):
    assert client.get("/login").status_code == 200
    response = auth.login()
    assert response.headers["Location"] == "/"

    with client:
        client.get("/")
        assert session["user_id"] == 1
        assert g.user["username"] == "test"


@pytest.mark.parametrize(
    ("username", "password", "message"),
    (
        ("a", "test", b"invalid username and/or password"),
        ("test", "a", b"invalid username and/or password"),
    ),
)
def test_login_validate_input(auth, username, password, message):
    response = auth.login(username, password)
    assert message in response.data


def test_logout(client, auth):
    auth.login()

    with client:
        auth.logout()
        assert "user_id" not in session


@pytest.mark.parametrize(
    "path",
    (
        "/",
        "/upload",
    ),
)
def test_login_required(client, path):
    response = client.post(path)
    assert response.headers["Location"] == "/login"


def test_account_get(client, auth):
    auth.login()
    res = client.get("/account")
    assert res.status_code == 200
    assert b"Account:" in res.data  # page renders for logged-in users


def test_account_change_password(client, auth):
    auth.login()
    # wrong old password
    res = client.post(
        "/account",
        data={"old": "wrong", "new": "Newpass1!", "confirm": "Newpass1!"},
        follow_redirects=True,
    )
    assert b"Old password incorrect" in res.data

    # correct flow
    res = client.post(
        "/account",
        data={"old": "test", "new": "Newpass1!", "confirm": "Newpass1!"},
        follow_redirects=True,
    )
    assert res.status_code == 200  # redirect back to index

    # verify new password works, old doesn’t
    auth.logout()
    bad = auth.login(password="test")
    assert b"invalid username and/or password" in bad.data
    good = auth.login(password="Newpass1!")
    assert good.status_code == 302 and good.headers["Location"] == "/"
