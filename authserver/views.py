import authserver
import flask


@authserver.app.route("/")
def show_index():
    """render index page"""
    with authserver.app.app_context():
        # logname must exist in session
        logname = authserver.model.check_session()
        if not logname:
            return flask.redirect("/login/")

        context = {
            # "logname": logname,
            # "logname_link": f"/users/{logname}/"
        }

    return flask.render_template("index.html", **context)


@authserver.app.route("/schema/", method=["POST"])
def upload_schema():
    with insta485.app.app_context():
        connection = authserver.model.get_db()

        # logname must exist in session
        logname = ""
        if 'logname' not in session:
            return redirect("/accounts/login/")
        logname = session['logname']

        target = flask.request.args.get('target')
        if target is None or target == "":
            target = "/"

        operation = flask.request.form.get('operation')
        if operation == "create":
            fileobj = flask.request.files.get('schema')  # or file
            filename = flask.request.form.get('dbname')
            if fileobj is None:
                abort(400)

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
                abort(404)
            elif post[0]['owner'] != logname:
                abort(403)
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
            abort(400)

    return redirect(target)
    