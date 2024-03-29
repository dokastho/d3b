"""Package node initializer."""
import flask
from d3b_client.client import *
# app is a single object used by all the code modules in this package
app = flask.Flask(__name__)  # pylint: disable=invalid-name
# Read settings from config module (site/config.py)
app.config.from_object('schemaserver.config')
# Overlay settings read from a Python file whose path is set in the environment
# variable SITE_SETTINGS. Setting this environment variable is optional.
# Docs: http://flask.pocoo.org/docs/latest/config/
#
# EXAMPLE:
# $ export SITE_SETTINGS=secret_key_config.py
app.config.from_envvar('SITE_SETTINGS', silent=True)


from schemaserver.views import *
from schemaserver.accounts import *
from schemaserver.api import *
from schemaserver.model import *
from schemaserver.schema import *
from schemaserver.utils import *