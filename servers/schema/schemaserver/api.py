import schemaserver
import flask
import os


@schemaserver.app.route('/api/v1/whoami/', methods=["POST"])
def get_account_info():
    """Return a json with logname"""

    data = {
        "logname": "",
        "schemas": []
    }
    if "logname" in flask.session:
        logname = flask.session["logname"]
        data["logname"] = logname
    
    req_data = {
        "table": "schemas",
        "query": "SELECT * FROM tables WHERE owner = ?",
        "args": [logname]
    }
    req_hdrs = {
        'content_type': 'application/json'
    }
        
    post = schemaserver.db.get(req_data, req_hdrs)

    data["schemas"] = post

    return flask.jsonify(data), 201

