import flask
import json
import uuid
import pathlib

def get_body() -> json:
    content_type = flask.request.headers.get('Content-Type')
    body: json
    if content_type == 'application/json':
        body = flask.request.json
    else:
        flask.abort(400)
        pass
    return body


def get_uuid(filename):
    """Get image uuid."""
    stem = uuid.uuid4().hex
    suffix = pathlib.Path(filename).suffix
    uuid_basename = f"{stem}{suffix}"

    return uuid_basename
