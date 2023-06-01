"""Test uploading functions."""

import os
import uuid
import pathlib
from tests.common import *


def test_upload():
    """Upload a file and ensure that it returns OK."""
    filename = "test_blob.bin"
    fpath = ROOT / filename
    fileobj = open(fpath, 'rb')

    # create id for media
    fileid = f'test-{get_uuid(filename)}'
    
    # make post request
    req_data = {
        "table": "schemas",
        "query": "INSERT INTO tables (owner, name, fileid) VALUES (?, ?, ?)",
        "args": [LOGNAME, filename, fileid],
        "media_op": "upload",
        "file_id": fileid
    }
    
    C.file_post(req_data, fileobj)
    
    # cleanup
    try:
        os.remove(ROOT.parent / 'var' / fileid)
    except:
        pass
    pass


def test_get():
    """Upload a file and ensure that subsequent get()'s return it."""
    filename = "test_blob.bin"
    fpath = ROOT / filename
    fileobj = open(fpath, 'rb')

    # create id for media
    fileid = f'test-{get_uuid(filename)}'
    
    # make post request
    req_data = {
        "table": "schemas",
        "query": "INSERT INTO tables (owner, name, fileid) VALUES (?, ?, ?)",
        "args": [LOGNAME, filename, fileid],
        "media_op": "upload",
        "file_id": fileid
    }
    
    C.file_post(req_data, fileobj)
    
    # get
    req_data = {
        "table": "schemas",
        "query": "",
        "args": [],
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
    
    # cleanup
    try:
        os.remove(ROOT.parent / 'var' / fileid)
    except:
        pass
    pass


def test_delete():
    """Upload a file and then delete it."""
    
    filename = "test_blob.bin"
    fpath = ROOT / filename
    fileobj = open(fpath, 'rb')

    # create id for media
    fileid = f'test-{get_uuid(filename)}'
    
    # make post request
    req_data = {
        "table": "schemas",
        "query": "INSERT INTO tables (owner, name, fileid) VALUES (?, ?, ?)",
        "args": [LOGNAME, filename, fileid],
        "media_op": "upload",
        "file_id": fileid
    }
    
    C.file_post(req_data, fileobj)
    
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
            
    C.post(req_data, req_hdrs)
    pass
