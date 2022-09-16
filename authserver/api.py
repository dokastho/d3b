import authserver
import flask
import os


@authserver.app.route('/api/v1/whoami/', methods=["POST"])
def get_account_info():
    """Return a json with logname"""

    data = {
        "logname": "",
        "schemas": []
    }
    if "logname" in flask.session:
        logname = flask.session["logname"]
        data["logname"] = logname
    
    database = authserver.model.get_db()
    cur = database.execute(
        "SELECT * "
        "FROM schemas "
        "WHERE owner == ?",
        (logname,)
    )
    schemas = cur.fetchall()

    data["schemas"] = schemas

    return flask.jsonify(data), 201

@authserver.app.route("/schema/delete/<id>/", methods=["POST"])
def delete_schema(id):
    with authserver.app.app_context():
        connection = authserver.model.get_db()

        # logname must exist in flask.session
        logname = ""
        if 'logname' not in flask.session:
            return flask.redirect("/accounts/login/")
        logname = flask.session['logname']

        # get post, delete filename, delete post
        cur = connection.execute(
            "SELECT * "
            "FROM schemas "
            "WHERE id == ?",
            (id,)
        )
        post = cur.fetchall()
        if len(post) == []:
            flask.abort(404)
        elif post[0]['owner'] != logname:
            flask.abort(403)
        post = post[0]

        # remove file
        os.remove(os.path.join(
            authserver.app.config['UPLOAD_FOLDER'],
            post['fileid'])
        )

        # delete entry
        cur = connection.execute(
            "DELETE "
            "FROM schemas "
            "WHERE id == ?",
            (id,)
        )
        cur.fetchall()
        
        return flask.Response(status=204)