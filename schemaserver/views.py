import schemaserver
import flask


@schemaserver.app.route("/")
def show_index():
    """render index page"""
    with schemaserver.app.app_context():
        # logname must exist in session
        logname = schemaserver.model.check_session()
        if not logname:
            return flask.redirect("/accounts/login/")

        context = {
            # "logname": logname,
            # "logname_link": f"/users/{logname}/"
        }

    return flask.render_template("index.html", **context)


@schemaserver.app.route("/user/<uname>/")
def show_user(uname):
    """Show profile options for uname."""
    logname = schemaserver.model.check_session()
    if not logname:
        return flask.redirect("/accounts/login/")

    if logname != uname:
        return flask.abort(403)

    context = {
        "logname": logname
    }
    

    return flask.render_template("accounts.html", **context)


