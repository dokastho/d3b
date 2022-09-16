import authserver
import flask


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
            if fileobj is None:
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
    