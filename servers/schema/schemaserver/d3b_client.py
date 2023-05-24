"""Client object for interfacing with d3b database."""

import requests
import json
import flask

class d3b_client:
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

