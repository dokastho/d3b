"""Test uploading functions."""

import os
import uuid
import pathlib
from tests.d3b_client import d3b_client

c = d3b_client()
logname = "dokastho"
root = pathlib.Path(__file__).parent


def get_uuid(filename):
    """Get image uuid."""
    stem = uuid.uuid4().hex
    suffix = pathlib.Path(filename).suffix
    uuid_basename = f"{stem}{suffix}"

    return uuid_basename


def test_upload():
    """Upload a file and ensure that it returns OK."""
    filename = "test_blob.bin"
    fpath = root / filename
    fileobj = open(fpath, 'rb')

    # create id for media
    fileid = f'test-{get_uuid(filename)}'
    
    # make post request
    req_data = {
        "table": "schemas",
        "query": "INSERT INTO tables (owner, name, fileid) VALUES (?, ?, ?)",
        "args": [logname, filename, fileid],
        "media_op": "upload",
        "file_id": fileid
    }
    
    c.file_post(req_data, fileobj)
    
    # cleanup
    try:
        os.remove(root.parent / 'var' / fileid)
    except:
        pass
    pass


def test_get():
    """Upload a file and ensure that subsequent get()'s return it."""
    pass


def test_delete():
    """Upload a file and then delete it."""
    
    filename = "test_blob.bin"
    fpath = root / filename
    fileobj = open(fpath, 'rb')

    # create id for media
    fileid = f'test-{get_uuid(filename)}'
    
    # make post request
    req_data = {
        "table": "schemas",
        "query": "INSERT INTO tables (owner, name, fileid) VALUES (?, ?, ?)",
        "args": [logname, filename, fileid],
        "media_op": "upload",
        "file_id": fileid
    }
    
    c.file_post(req_data, fileobj)
    
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
            
    c.post(req_data, req_hdrs)
    pass
