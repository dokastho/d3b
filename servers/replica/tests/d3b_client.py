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
        payload = {
            'json': (None, json.dumps(data), 'application/json'),
            'file': (fileobj, fileobj.name.split('/')[-1])
        }
        response = replicaserver.app.test_client().post(data=payload)
        if response.status_code != 200:
            flask.abort(500)
        pass

