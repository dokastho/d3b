#!/bin/python3

import flask
import schemaserver

app = schemaserver.app

if __name__ == "__main__":
    app.run(port=5056)
