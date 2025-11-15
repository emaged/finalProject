import os
import tempfile

import pytest
from dbbv import create_app
from dbbv.db import get_db, init_db

with open(os.path.join(os.path.dirname(__file__), 'data.sql'), 'rb') as f:
    _data_sql = f.read().decode('utf8')


@pytest.fixture
def app():
    db_fd, db_path = tempfile.mkstemp()

    app = create_app({
        'TESTING': True,
        'DATABASE': db_path,
        'WTF_CSRF_ENABLED': False,
    })
    
    test_upload_dir = os.path.join(app.instance_path, 'test_user_databases')
    os.makedirs(test_upload_dir, exist_ok=True)
    
    # override upload folder
    app.config['UPLOAD_FOLDER'] = test_upload_dir
    
    # override session storage too
    from cachelib import FileSystemCache
    app.config['SESSION_CACHELIB'] = FileSystemCache(test_upload_dir)

    with app.app_context():
        init_db()
        get_db().executescript(_data_sql)

    yield app

    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def runner(app):
    return app.test_cli_runner()


### authentication ###
class AuthActions(object):
    def __init__(self, client):
        self._client = client

    def login(self, username='test', password='test'):
        return self._client.post(
            '/login',
            data={'username': username, 'password': password}
        )

    def logout(self):
        return self._client.get('/logout')


@pytest.fixture
def auth(client):
    return AuthActions(client)