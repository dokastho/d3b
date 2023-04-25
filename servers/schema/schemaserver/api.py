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
    
    database = schemaserver.model.get_db()
    cur = database.execute(
        "SELECT * "
        "FROM schemas "
        "WHERE owner == ?",
        (logname,)
    )
    schemas = cur.fetchall()

    data["schemas"] = schemas

    return flask.jsonify(data), 201

