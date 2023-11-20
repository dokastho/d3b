import replicaserver
import sqlite3
import flask
import os
from random import randint
from pydrpc.drpc_client import *
from d3b_client.client import *


def dict_factory(cursor, row):
    """Convert database row objects to a dictionary keyed on column name.

    This is useful for building dictionaries which are then used to render a
    template.  Note that this would be inefficient for large queries.
    """
    return {col[0]: row[idx] for idx, col in enumerate(cursor.description)}


def get_db(table_id: str):
    """Open a new database connection.

    Flask docs:
    https://flask.palletsprojects.com/en/1.0.x/appcontext/#storing-data
    """
    if 'sqlite_db' not in flask.g:
        db_path = replicaserver.app.config['UPLOAD_FOLDER']
        db_filename = db_path / table_id
        flask.g.sqlite_db = sqlite3.connect(str(db_filename))
        flask.g.sqlite_db.row_factory = dict_factory
        # Foreign keys have to be enabled per-connection.  This is an sqlite3
        # backwards compatibility thing.
        flask.g.sqlite_db.execute("PRAGMA foreign_keys = ON")
    return flask.g.sqlite_db


def get_table_uuid(table):
    """Get table uuid."""

    # set up connection with translational table
    db_path = replicaserver.app.config['UPLOAD_FOLDER']
    db_filename = db_path / "schemas.sqlite3"
    connection = sqlite3.connect(str(db_filename))
    connection.row_factory = dict_factory
    # Foreign keys have to be enabled per-connection.  This is an sqlite3
    # backwards compatibility thing.
    connection.execute("PRAGMA foreign_keys = ON")

    # fetch uuid
    cur = connection.execute(
        "SELECT fileid FROM tables WHERE name = ?",
        (table,)
    )
    uuid = cur.fetchone()
    if uuid is None:
        connection.close()
        raise Exception()

    # close
    connection.commit()
    connection.close()

    return uuid['fileid']


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

    # perform database operation
    try:
        body = Op.data
        table_uuid = get_table_uuid(body["table"])
        connection = get_db(table_uuid)
        cur = connection.execute(body["query"], body["args"])
        data = cur.fetchall()
    except:
        if Op.data is None:
            Op.data = dict()
            pass
        Op.data["error"] = "not applied"
        return Op.data

    close_db(None)

    # if there's a media upload, get blob & save it
    if "media_op" in body:
        file_id = body["file_id"]
        op = body["media_op"]

        # upload
        if op == "upload":
            host_id = body["host_id"]
            my_id = replicaserver.app.config["MY_HOST_ID"]
            blob = None
            blob_path = replicaserver.app.config["UPLOAD_FOLDER"]/file_id
            if host_id != my_id:
                # get blob from peer
                peer_host = f"https://d3b{host_id}.dokastho.io"
                c = d3b_client(peer_host)

                req_data = {
                    "table": "schemas",
                    "query": "",
                    "args": [],
                    "media_op": "get",
                    "file_id": file_id
                }
                req_hdrs = {
                    'content_type': 'application/json'
                }

                blob = c.file_get(req_data, req_hdrs)
                # save file
                with open(blob_path, "wb") as fp:
                    fp.write(blob)
                    pass
                pass
            else:
                blob = flask.request.files.get('file')
                # save file
                blob.save(blob_path)
                pass
            pass
        # delete
        elif op == "delete":
            # delete file
            blob_path = replicaserver.app.config["UPLOAD_FOLDER"]/file_id
            os.remove(blob_path)
            pass

        pass

    return data


def add_op(Op: replicaserver.d3b_op):
    """perform db updates until after request is returned"""

    replicaserver.seq_lock.acquire()
    # want assigned host
    dh = drpc_host()
    hosts = replicaserver.app.config["PAXOS_HOSTS"]
    host_idx = replicaserver.app.config["MY_HOST_ID"] - 1
    dh.hostname = hosts[host_idx]
    dh.port = replicaserver.app.config["PAXOS_PORTS"][host_idx]

    # request
    d3b_req = Op

    # reply
    d3b_rep = replicaserver.d3b_op()

    # RPC
    req = drpc_arg_wrapper(d3b_req)
    rep = drpc_arg_wrapper(d3b_rep)
    m = drpc_msg()
    m.req = req
    m.rep = rep
    m.target = replicaserver.app.config["PAXOS_ENDPOINT"]

    c = drpc_client(timeout_val=replicaserver.app.config["TIMEOUT_VAL"])
    logged = False
    data = dict()
    while not logged:
        m.req.args.seq = replicaserver.seq
        m.rep.args.err = 1
        replicaserver.seq += 1
        while m.rep.args.err == 1:
            err = c.Call(dh, m)
            if err == -1:
                print("error reaching paxos servers")
                exit(1)
            pass
        if m.rep.args.err == 2:
            # forgotten
            continue
            
        logged = True
        data = apply_op(m.rep.args)
        log_data = {
            "request" : {
                "seq": m.req.args.seq,
                "seed": m.req.args.seed,
                "op": m.req.args.data
            },
            "reply" : {
                "seq": m.rep.args.seq,
                "seed": m.rep.args.seed,
                "op": m.rep.args.data
            },
        }
        replicaserver.my_logger.log(json.dumps(log_data) )

        # continue logging if the value returned isn't the one we requested to log
        if m.rep.args.seed != m.req.args.seed:
            logged = False
            continue

        pass
    replicaserver.seq_lock.release()
    return data
