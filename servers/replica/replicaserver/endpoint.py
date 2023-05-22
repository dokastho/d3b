"""Endpoints for requests to a replica."""

import flask
import json
import replicaserver
from pydrpc.drpc_client import *


@replicaserver.app.route("/", methods=["POST"])
def parse_request():
    # get data from body
    content_type = flask.request.headers.get('Content-Type')
    body: json
    if (content_type == 'application/json'):
        body = flask.request.json
    else:
        flask.abort(400)
        pass

    # verify validity of request body
    if ["table", "query", "args"] not in body:
        flask.abort(400)
        pass
    
    table = body["table"]
    query = body["query"]
    args = body["args"]
    op = replicaserver.d3b_op(table, query, args)

    # record this request in the paxos log
    data = replicaserver.add_op(op)

    return flask.jsonify(data)
