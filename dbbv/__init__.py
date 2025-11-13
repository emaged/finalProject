import os

from flask import Flask
from flask_wtf.csrf import CSRFProtect
from cachelib import FileSystemCache

csrf = CSRFProtect()

def create_app(test_config=None):
    # create and configure app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY = 'DEV',
        DATABASE = os.path.join(app.instance_path, 'dbbv.sqlite'),
        UPLOAD_FOLDER = os.path.join(app.instance_path, 'user_databases'),
        SESSION_PERMANENT = False,
        SESSION_TYPE = 'cachelib',     
        # not used but for future setup
        MAX_CONTENT_LENGTH = 16 * 1024 * 1024,
    )
            
    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)
        
    # init csrf    
    csrf.init_app(app)

    # ensure the instance folder exists
    os.makedirs(app.instance_path, exist_ok=True)
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # set up session_cache after UPLOAD_FOLDER has been defined 
    app.config["SESSION_CACHE"] = FileSystemCache(app.config["UPLOAD_FOLDER"])
    
    from flask_session import Session
    Session(app)
        
    # initialise db
    from . import db
    db.init_app(app)
    
    # import & register blueprints
    from dbbv.routes import auth
    app.register_blueprint(auth.bp)
    from dbbv.routes import sqlite_routes
    app.register_blueprint(sqlite_routes.bp)
    
    from dbbv.routes.sqlite_routes import close_custom_db
    app.teardown_appcontext(close_custom_db)
    
    from dbbv.routes import alchemy_routes
    app.register_blueprint(alchemy_routes.bp)
    from dbbv.routes import files
    app.register_blueprint(files.bp)
    
    
    from dbbv.routes.helpers import split_ext
    app.jinja_env.globals.update(split_ext=split_ext)

    return app

