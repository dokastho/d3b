"""Test applying operations in a group setting."""

import os
from tests.test_d3b_client import d3b_client
from tests.common import *


def test_group():
    """Upload an image to one server, get it from another, delete it and flush log."""

    alt_host = d3b_client("https://d3b1.dokasfam.com")
    # alt_host = d3b_client("https://dev2.dokasfam.com")

    filename = "test_blob.bin"
    fpath = ROOT / filename
    fileobj = open(fpath, 'rb')

    # create id for media
    fileid = f'test-{get_uuid(filename)}'
    
    # upload image to other host
    req_data = {
        "table": "schemas",
        "query": "INSERT INTO tables (owner, name, fileid) VALUES (?, ?, ?)",
        "args": [LOGNAME, filename, fileid],
        "media_op": "upload",
        "file_id": fileid
    }
    
    alt_host.file_post(req_data, fileobj) # Fail here? Check that ./wsgi.py 1 is running
    
    # get from test host
    req_data = {
        "table": "schemas",
        "query": "SELECT * from tables WHERE fileid = ?",
        "args": [fileid],
        "media_op": "get",
        "file_id": fileid
    }
    req_hdrs = {
        'content_type': 'application/json'
    }

    data = C.file_get(req_data, req_hdrs)
    
    with open(fpath, 'rb') as fp:
        assert data == fp.read()
        pass
    
    # delete
    req_data = {
        "table": "schemas",
        "query": "DELETE FROM tables WHERE fileid = ?",
        "args": [fileid],
        "media_op": "delete",
        "file_id": fileid
    }
    req_hdrs = {
        'content_type': 'application/json'
    }
    
    alt_host.post(req_data, req_hdrs)

    # flush log for both
    req_data = {
        "table": "schemas",
        "query": "SELECT * FROM tables WHERE owner = ?",
        "args": [LOGNAME]
    }
    req_hdrs = {
        'content_type': 'application/json'
    }

    data1 = alt_host.get(req_data, req_hdrs)
    
    # file was deleted?
    
    assert not fileid in os.listdir(ROOT.parent / "var")
    
    # replace it and try again
    with open(ROOT.parent / "var" / fileid, "wb") as fp:
        fp.write(data)
        pass
    
    data2 = C.get(req_data, req_hdrs)

    # assert file deleted again
    
    assert not fileid in os.listdir(ROOT.parent / "var")
    
    # assert return same
    assert data1 == data2
    pass
    