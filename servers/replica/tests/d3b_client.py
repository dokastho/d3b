"""Client object for interfacing with d3b database."""

import json
import flask
import replicaserver

class d3b_client:

    def get(self, data: json, headers):
        response = replicaserver.app.test_client().post(json=data, headers=headers)
        if response.status_code != 200:
            flask.abort(500)
        return response.json
    
    def post(self, data, headers):
        response = replicaserver.app.test_client().post(json=data, headers=headers)
        if response.status_code != 200:
            flask.abort(500)
        pass
    
    def file_post(self, data, fileobj):
        files = {
            'json': (None, json.dumps(data), 'application/json'),
            'file': fileobj
        }
        response = replicaserver.app.test_client().post(files=files)
        if response.status_code != 200:
            flask.abort(500)
        pass

