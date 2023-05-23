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
    op = replicaserver.d3b_op(table, query, args)

    # record this request in the paxos log
    data = replicaserver.add_op(op)

    # if there's media, deal with it
    if "filename" in body:
        if "fileop" not in body:
            flask.abort(400)
            pass
        file_op = body['fileop']
        file_name = body['file_name']

        # get uuid of the file
        file_id = replicaserver.get_uuid()

        if file_op == "get":
            pass
        elif file_op == "upload":
            blob = flask.request.files.get('file')

            # save file
            path = replicaserver.app.config["UPLOAD_FOLDER"]/file_id
            blob.save(path)
            pass
        elif file_op == "delete":
            # delete file
            os.remove(os.path.join(
                replicaserver.app.config['UPLOAD_FOLDER'],
                file_id)
            )
            pass

        pass

    return flask.jsonify(data)
