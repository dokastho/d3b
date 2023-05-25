"""Endpoints for requests to a replica."""

import flask
import replicaserver
import json
import io


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
    
    # if media in request, ensure request has requisite info
    if "media_op" in body:
        for arg in ["file_id", "host_id"]:
            if arg not in body:
                flask.abort(400)
                pass
            pass
        # mark which host submitted this
        body["host_id"] = replicaserver.app.config["MY_HOST_ID"]
        pass

    op = replicaserver.d3b_op(body)

    # record this request in the paxos log
    data = replicaserver.add_op(op)
    
    # media op get should only be applied if it was the latest request
    if "media_op" in body and body["media_op"] == "get":
        # use the 'data' returned from db
        file_id = body['file_id']
        fileobj = open(replicaserver.app.config["UPLOAD_FOLDER"] / file_id, 'rb')
        return flask.Response(fileobj)

    return flask.jsonify(data)
