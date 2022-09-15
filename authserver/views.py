import authserver
import flask

@authserver.app.route("/")
def show_index():
    """render index page"""
    with authserver.app.app_context():
        # logname must exist in session
        # logname = auth_server.model.check_session()
        # if not logname:
            # return flask.redirect("/accounts/login/")

        context = {
            # "logname": logname,
            # "logname_link": f"/users/{logname}/"
        }

    return flask.render_template("index.html", **context)