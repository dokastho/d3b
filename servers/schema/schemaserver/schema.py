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
                "args": [logname, filename, fileid],
                "media_op": "upload",
                "file_id": fileid
            }
            
            schemaserver.get_client().file_post(req_data, fileobj)

        else:
            flask.abort(400)

    return flask.redirect(target)
    
@schemaserver.app.route("/schema/delete/", methods=["POST"])
def delete_schema():
    with schemaserver.app.app_context():
        if 'dbid' not in flask.request.args:
            flask.abort(400)
        if 'fileid' not in flask.request.args:
            flask.abort(400)
            
        db_id = flask.request.args['dbid']
        file_id = flask.request.args['fileid']

        # logname must exist in flask.session
        logname = ""
        if 'logname' not in flask.session:
            return flask.redirect("/accounts/login/")
        logname = flask.session['logname']
        
        # get post, delete filename, delete post
        req_data = {
            "table": "schemas",
            "query": "SELECT * FROM tables WHERE id = ?",
            "args": [db_id]
        }
        req_hdrs = {
            'content_type': 'application/json'
        }
            
        post = schemaserver.get_client().get(req_data, req_hdrs)

        if len(post) == []:
            flask.abort(404)
        elif post[0]['owner'] != logname:
            flask.abort(403)
        post = post[0]

        # delete entry
        req_data = {
            "table": "schemas",
            "query": "DELETE FROM tables WHERE id = ?",
            "args": [db_id],
            "media_op": "delete",
            "file_id": file_id
        }
        req_hdrs = {
            'content_type': 'application/json'
        }
            
        schemaserver.get_client().post(req_data, req_hdrs)
        
        return flask.Response(status=204)

@schemaserver.app.route("/schema/<name>/")
def show_schema(name):
    """render schema page"""