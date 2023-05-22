"""Endpoints for requests to a replica."""

import flask
import json
import replicaserver
from random import randint
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

    # record this request in the paxos log
    # want random host
    dh = drpc_host()
    hosts = replicaserver.app.config["PAXOS_HOSTS"]
    host_idx = randint(0, len(hosts) - 1)
    dh.hostname = hosts[host_idx]
    dh.port = replicaserver.app.config["PAXOS_PORTS"][host_idx]

    # request
    table = body["table"]
    query = body["query"]
    args = body["args"]
    d3b_req = replicaserver.d3b_op(table, query, args)

    # reply
    d3b_rep = replicaserver.d3b_op()

    # RPC
    req = drpc_arg_wrapper(d3b_req)
    rep = drpc_arg_wrapper(d3b_rep)
    m = drpc_msg()
    m.req = req
    m.rep = rep
    m.target = replicaserver.app.config["PAXOS_ENDPOINT"]
    data = replicaserver.await_reply(dh, m)

    return flask.jsonify(data)
