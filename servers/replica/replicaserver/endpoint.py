"""Endpoints for requests to a replica."""

import flask
import replicaserver
import os


@replicaserver.app.route("/", methods=["POST"])
def parse_request():
    # get data from body
    body = replicaserver.get_body()

    # verify validity of request body
    for arg in ["table", "query", "args"]:
        if arg not in body:
            flask.abort(400)
            pass
        pass

    table = body["table"]
    query = body["query"]
    args = body["args"]
    flags = []
    if "flags" in body:
        flags = body["flags"]
        pass
    op = replicaserver.d3b_op(table, query, args, flags)

    # record this request in the paxos log
    data = replicaserver.add_op(op)

    return flask.jsonify(data)
