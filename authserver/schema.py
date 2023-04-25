import authserver
import flask
import os


@authserver.app.route("/schema/", methods=["POST"])
def upload_schema():
    with authserver.app.app_context():
        connection = authserver.model.get_db()

        # logname must exist in flask.session
        logname = ""
        if 'logname' not in flask.session:
            return flask.redirect("/accounts/login/")
        logname = flask.session['logname']

        target = flask.request.args.get('target')
        if target is None or target == "":
            target = "/"

        operation = flask.request.form.get('operation')
        if operation == "create":
            fileobj = flask.request.files.get('file')
            filename = flask.request.form.get('dbname')
            if fileobj is None or not fileobj.filename.endswith('.sql'):
                flask.abort(400)

            # save image
            fileid = authserver.model.get_uuid(fileobj.filename)
            path = authserver.app.config["UPLOAD_FOLDER"]/fileid
            fileobj.save(path)

            # insert new posts entry
            cur = connection.execute(
                "INSERT INTO schemas "
                "(owner, name, fileid) "
                "VALUES (?, ?, ?)",
                (logname, filename, fileid,)
            )
            cur.fetchone()

        else:
            flask.abort(400)

    return flask.redirect(target)
    
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

@authserver.app.route("/schema/<name>/")
def show_schema(name):
    """render schema page"""