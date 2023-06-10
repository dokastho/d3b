#!/bin/python3

import flask
import replicaserver
import sys

app = replicaserver.app

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("need to supply host_id argument.")
        exit()
    host_id = int(sys.argv[1])
    app.config["MY_HOST_ID"] = host_id
    app.config["UPLOAD_FOLDER"] = app.config["SITE_ROOT"]/f'var-{host_id}'
    app.run(port=8054 + host_id)
    pass
