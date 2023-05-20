"""Endpoints for requests to a replica."""

import flask
import json
import replicaserver
import grpc

@replicaserver.app.route("/")
def parse_request():
    # get data from body
    content_type = flask.request.headers.get('Content-Type')
    body: json
    if (content_type == 'application/json'):
        body = flask.request.json
    else:
        flask.abort(400)
        pass
    
    # record this request in the paxos log
    
    # perform db updates until this request is returned
    
     
    return flask.Response(status=204)
