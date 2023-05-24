#!/bin/python3

import flask
import replicaserver
import sys

app = replicaserver.app

if __name__ == "__main__":
    if len(sys.argv) == 2:
        host_id = int(sys.argv[1])
        app.config["MY_HOST_ID"] = host_id
        pass
    app.run(port=5055)
