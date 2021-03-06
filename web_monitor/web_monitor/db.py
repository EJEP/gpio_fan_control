"""Set up how to talk to the database. This follows the flask tutorial way of
doing things."""

import sqlite3

from flask import current_app, g
from flask.cli import with_appcontext


def get_db():
    if 'db' not in g:
        print(current_app.config['DB_LOCATION'])
        g.db = sqlite3.connect(
            current_app.config['DB_LOCATION'],
            detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES
        )
        g.db.row_factory = sqlite3.Row

    return g.db


def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()


def init_app(app):
    app.teardown_appcontext(close_db)
