import replicaserver
import sqlite3
import flask
from pydrpc.drpc_client import *


def dict_factory(cursor, row):
    """Convert database row objects to a dictionary keyed on column name.

    This is useful for building dictionaries which are then used to render a
    template.  Note that this would be inefficient for large queries.
    """
    return {col[0]: row[idx] for idx, col in enumerate(cursor.description)}


def get_db(table: str):
    """Open a new database connection.

    Flask docs:
    https://flask.palletsprojects.com/en/1.0.x/appcontext/#storing-data
    """
    if 'sqlite_db' not in flask.g:
        db_path = replicaserver.app.config['DATABASE_PATH']
        db_filename = db_path / f'{table}.sqlite3'
        flask.g.sqlite_db = sqlite3.connect(str(db_filename))
        flask.g.sqlite_db.row_factory = dict_factory
        # Foreign keys have to be enabled per-connection.  This is an sqlite3
        # backwards compatibility thing.
        flask.g.sqlite_db.execute("PRAGMA foreign_keys = ON")
    return flask.g.sqlite_db


@replicaserver.app.teardown_appcontext
def close_db(error):
    """Close the database at the end of a request.

    Flask docs:
    https://flask.palletsprojects.com/en/1.0.x/appcontext/#storing-data
    """
    assert error or not error  # Needed to avoid superfluous style error
    sqlite_db = flask.g.pop('sqlite_db', None)
    if sqlite_db is not None:
        sqlite_db.commit()
        sqlite_db.close()


def apply_op(Op: replicaserver.d3b_op):
    """Apply a database operation returned from the paxos process."""
    replicaserver.seq_lock.acquire()
    
    # if the Op is a media upload, get from other servers
    # multicast get request
    # TODO

    # perform database operation
    connection = get_db(Op.table)
    cur = connection.execute(Op.query, Op.args)
    data = cur.fetchall()

    replicaserver.seq_lock.release()
    return data


def get_seq_num() -> int:
    replicaserver.seq_lock.acquire()

    seq = replicaserver.seq_num

    replicaserver.seq_lock.release()
    return seq


def await_reply(dh: drpc_host, m: drpc_msg):
    """perform db updates until after request is returned"""
    c = drpc_client()
    logged = False
    data = dict()
    while not logged:
        c.Call(dh, m)
        logged = True
        data = apply_op(m.rep.args)

        # continue logging if the value returned isn't the one we requested to log
        if m.rep.args.seed != m.req.args.seed:
            logged = False
            continue

        pass
    return data
