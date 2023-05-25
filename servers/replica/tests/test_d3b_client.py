"""Client object for interfacing with d3b database."""

import json
import flask
import replicaserver
import io
import requests

class test_d3b_client:

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
    
    def file_get(self, data: json, headers):
        response = replicaserver.app.test_client().post(json=data, headers=headers)
        if response.status_code != 200:
            flask.abort(500)
        return response.data
    
    def file_post(self, data, fileobj):
        payload = {
            'json': (io.BytesIO(json.dumps(data).encode("ascii")), None, 'application/json'),
            'file': (fileobj, 'test.jpg')
        }
        response = replicaserver.app.test_client().post(data=payload)
        if response.status_code != 200:
            flask.abort(500)
        pass

class d3b_client:
    """Copied from d3b_client package."""
    host: str
    
    def __init__(self, host: str) -> None:

        self.host = host
        pass

    def get(self, data: json, headers):
        response = requests.post(self.host, json=data, headers=headers)
        if response.status_code != 200:
            flask.abort(500)
        return response.json()
    
    def post(self, data, headers):
        response = requests.post(self.host, json=data, headers=headers)
        if response.status_code != 200:
            flask.abort(500)
        pass
    
    def file_get(self, data: json, headers):
        response = requests.post(self.host, json=data, headers=headers)
        if response.status_code != 200:
            flask.abort(500)
        return response.content
    
    def file_post(self, data, fileobj):
        files = {
            'json': (None, json.dumps(data), 'application/json'),
            'file': fileobj
        }
        response = requests.post(self.host, files=files)
        if response.status_code != 200:
            flask.abort(500)
        pass

