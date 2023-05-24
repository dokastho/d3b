"""Test applying operations in a group setting."""

import pathlib
from tests.common import *
from tests.d3b_client import d3b_client_at_host


def test_group():
    """Upload an image to one server, get it from another, delete it and flush log."""

    alt_host = d3b_client_at_host("https://d3b1.dokasfam.com")

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
    
    alt_host.file_post(req_data, fileobj)
    
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
    
    data2 = C.get(req_data, req_hdrs)
    
    assert data1 == data2
    pass
    