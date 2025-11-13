import pytest 

def test_index(client, auth):
    response = client.get('/', follow_redirects=True)
    assert b"Please sign in" in response.data
    assert b"Register" in response.data

    auth.login()
    response = client.get('/')
    assert b'Log Out' in response.data
    assert b'Account' in response.data
    assert b'File Upload' in response.data
    assert b'SQLite' in response.data
    assert b'SQLAlchemy' in response.data
    