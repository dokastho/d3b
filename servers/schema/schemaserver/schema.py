import schemaserver
import flask
import os


@schemaserver.app.route("/schema/", methods=["POST"])
def upload_schema():
    with schemaserver.app.app_context():
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
            if fileobj is None or not fileobj.filename.endswith('.sqlite3'):
                flask.abort(400)

            # create id for media
            fileid = schemaserver.model.get_uuid(fileobj.filename)
            
            # make post request
            req_data = {
                "table": "schemas",
                "query": "INSERT INTO tables (owner, name, fileid) VALUES (?, ?, ?)",
                "args": [logname, filename, fileid]
            }
            req_hdrs = {
                'content_type': 'application/json'
            }
            
            schemaserver.db.post(req_data, req_hdrs)

        else:
            flask.abort(400)

    return flask.redirect(target)
    
@schemaserver.app.route("/schema/delete/<id>/", methods=["POST"])
def delete_schema(id):
    with schemaserver.app.app_context():
        connection = schemaserver.model.get_db()

        # logname must exist in flask.session
        logname = ""
        if 'logname' not in flask.session:
            return flask.redirect("/accounts/login/")
        logname = flask.session['logname']
        
        # get post, delete filename, delete post
        req_data = {
            "table": "schemas",
            "query": "SELECT * FROM tables WHERE id = ?",
            "args": [id]
        }
        req_hdrs = {
            'content_type': 'application/json'
        }
            
        post = schemaserver.db.get(req_data, req_hdrs)

        if len(post) == []:
            flask.abort(404)
        elif post[0]['owner'] != logname:
            flask.abort(403)
        post = post[0]

        # remove file
        # os.remove(os.path.join(
        #     schemaserver.app.config['UPLOAD_FOLDER'],
        #     post['fileid'])
        # )

        # delete entry
        req_data = {
            "table": "schemas",
            "query": "DELETE FROM tables WHERE id = ?",
            "args": [id],
            "flags": [0b10000000]
        }
        req_hdrs = {
            'content_type': 'application/json'
        }
            
        schemaserver.db.post(req_data, req_hdrs)
        
        return flask.Response(status=204)

@schemaserver.app.route("/schema/<name>/")
def show_schema(name):
    """render schema page"""