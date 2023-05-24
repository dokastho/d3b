"""Test basic endpoint functions."""

import hashlib
from tests.common import *


def test_whoami():
    """Test get functionality using the whoami() logic from schema."""

    req_data = {
        "table": "schemas",
        "query": "SELECT * FROM tables WHERE owner = ?",
        "args": [LOGNAME]
    }
    req_hdrs = {
        'content_type': 'application/json'
    }
    
    post = C.get(req_data, req_hdrs)
    assert(len(post) > 0)
    
    # assert response content is (somewhat) valid
    for content in post:
        assert(list(content.keys()) == [
            'created',
            'fileid',
            'id',
            'name',
            'owner'
        ])
        pass
    pass

def test_login():
    """Test request-response functionality with the schema login process."""
    # schema must have username and password in headers
    username = "dokastho"
    password = "password"
    # verify username and password match an existing user

    req_data = {
        "table": "schemas",
        "query": "SELECT password FROM users WHERE username = ?",
        "args": [username],
    }
    req_hdrs = {
        'content_type': 'application/json'
    }
    
    pw_hash = C.get(req_data, req_hdrs)
    if len(pw_hash) == 0:
        assert(False)

    # get db entry salt if present and encrypt password
    pw_hash = pw_hash[0]
    salt = pw_hash['password'].split("$")
    if len(salt) > 1:
        salt = salt[1]
        pw_str = encrypt(salt, password)
    else:
        pw_str = password

    # find an entry with encrypted password
    req_data = {
        "table": "schemas",
        "query": "SELECT username FROM users WHERE username = ? AND password = ?",
        "args": [username, pw_str],
    }
    req_hdrs = {
        'content_type': 'application/json'
    }
        
    user = C.get(req_data, req_hdrs)
    if len(user) == 0:
        assert(False)
    
    assert(user == [{'username': 'dokastho'}])
    pass

