import authserver
import flask


@authserver.app.route("/schema/", methods=["POST"])
def upload_schema():
    with authserver.app.app_context():
        connection = authserver.model.get_db()

        # logname must exist in flask.session
        logname = ""
        if 'logname' not in flask.session:
            return redirect("/accounts/login/")
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

        elif operation == "delete":
            uploadid = flask.request.form.get('id')

            # get post, delete filename, delete post
            cur = connection.execute(
                "SELECT * "
                "FROM schemas "
                "WHERE id == ?",
                (uploadid,)
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
                (uploadid,)
            )
            cur.fetchall()

        else:
            flask.abort(400)

    return flask.redirect(target)
    