import os

from flask import Flask, session

def create_app(test_config=None):
    # create and configure app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='DEV',
        DATABASE=os.path.join(app.instance_path, 'dbbv.sqlite'),
        SESSION_PERMANENT = False,
        SESSION_TYPE = 'filesystem',     
        UPLOAD_FOLDER=os.path.join(app.instance_path, 'user_databases'),
        MAX_CONTENT_LENGTH = 16 * 1000 * 1000,
    )
        
    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)
        
    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass
    
    from flask_session import Session
    Session(app)
        
    # initialise db
    from . import db
    db.init_app(app)
    
    # import & register blueprints
    from dbbv.routes import auth
    app.register_blueprint(auth.bp)
    from dbbv.routes import sqlite
    app.register_blueprint(sqlite.bp)
    
    from dbbv.routes.sqlite import close_custom_db
    app.teardown_appcontext(close_custom_db)
    
    from dbbv.routes import alchemy
    app.register_blueprint(alchemy.bp)
    from dbbv.routes import files
    app.register_blueprint(files.bp)
    
    
    from dbbv.routes.helpers import split_ext
    app.jinja_env.globals.update(split_ext=split_ext)

    return app

