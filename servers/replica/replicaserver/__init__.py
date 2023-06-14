"""Package node initializer."""
import flask
from threading import Lock
# app is a single object used by all the code modules in this package
app = flask.Flask(__name__)  # pylint: disable=invalid-name
# Read settings from config module (site/config.py)
app.config.from_object('replicaserver.config')
# Overlay settings read from a Python file whose path is set in the environment
# variable SITE_SETTINGS. Setting this environment variable is optional.
# Docs: http://flask.pocoo.org/docs/latest/config/
#
# EXAMPLE:
# $ export SITE_SETTINGS=secret_key_config.py
app.config.from_envvar('SITE_SETTINGS', silent=True)

# shared lock
seq_lock = Lock()

# paxos seq num
seq = 0

from replicaserver.rpcs import *
from replicaserver.common import *
from replicaserver.model import *
from replicaserver.endpoint import *
from replicaserver.paxos import *