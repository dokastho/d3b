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
        for arg in ["file_id"]:
            if arg not in body:
                flask.abort(400)
                pass
            pass
        # mark which host submitted this
        body["host_id"] = replicaserver.app.config["MY_HOST_ID"]
        pass
    
        
    # media op get should not be linearized
    # abide by the following pattern for gets:
    # make a linearized request (1) for the file ID
    # then make a follow-up request for the file (2)
    # the former (1) request will update the paxos log
    # the latter (2) request will not contribute bloat
    if "media_op" in body and body["media_op"] == "get":
        # use the 'data' returned from db
        file_id = body['file_id']
        fileobj = open(replicaserver.app.config["UPLOAD_FOLDER"] / file_id, 'rb')
        return flask.Response(fileobj)

    op = replicaserver.d3b_op(json_data=body)

    # record this request in the paxos log
    data = replicaserver.add_op(op)

    return flask.jsonify(data)
