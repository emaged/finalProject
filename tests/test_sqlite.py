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

    # room for adding more testing of query input etc.
