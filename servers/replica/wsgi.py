#!/bin/python3

import flask
import replicaserver

app = replicaserver.app

if __name__ == "__main__":
    app.run(port=5055)
