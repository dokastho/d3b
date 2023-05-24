"""Endpoints for requests to a replica."""

import flask
import replicaserver


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

    op = replicaserver.d3b_op(body)

    # record this request in the paxos log
    data = replicaserver.add_op(op)
    
    # media op get should only be applied if it was the latest request
    # if replicaserver.MEDIA_REQUEST & op.flags != 0:
    #     # use the 'data' returned from db
    #     pass

    return flask.jsonify(data)
