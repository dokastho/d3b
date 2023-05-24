import flask
import json

def get_body() -> json:
    content_type = flask.request.headers.get('Content-Type')
    print(flask.request.data)
    body: json
    if content_type == 'application/json':
        body = flask.request.json
    else:
        body = json.loads(flask.request.form['json'])
        pass
    return body

