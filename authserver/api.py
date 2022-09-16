import authserver
import flask


@authserver.app.route('/api/v1/whoami/', methods=["POST"])
def get_whoami():
    """Return a json with logname"""

    data = {
        "logname": ""
    }
    if "logname" in flask.session:
        logname = flask.session["logname"]
        data["logname"] = logname

    return flask.jsonify(data), 201

        
