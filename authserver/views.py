import authserver
import flask


@authserver.app.route("/")
def show_index():
    """render index page"""
    with authserver.app.app_context():
        # logname must exist in session
        logname = authserver.model.check_session()
        if not logname:
            return flask.redirect("/accounts/login/")

        context = {
            # "logname": logname,
            # "logname_link": f"/users/{logname}/"
        }

    return flask.render_template("index.html", **context)


@authserver.app.route("/user/<uname>")
def show_user(uname):
    """Show profile options for uname."""
    logname = authserver.model.check_session()
    if not logname:
        return flask.redirect("/accounts/login/")

    if logname != uname:
        return flask.abort(403)

    context = {
        "logname": logname
    }
    

    return flask.render_template("accounts.html", **context)


