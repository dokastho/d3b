"""Test basic endpoint functions."""

import hashlib
from tests.d3b_client import d3b_client

c = d3b_client()

def encrypt(salt, password):
    """One way decryption given the plaintext pw and salt from user db."""
    algorithm = 'sha512'

    hash_obj = hashlib.new(algorithm)
    password_salted = salt + password
    hash_obj.update(password_salted.encode('utf-8'))
    password_hash = hash_obj.hexdigest()
    password_db_string = "$".join([algorithm, salt, password_hash])
    return password_db_string

def test_whoami():
    """Test get functionality using the whoami() logic from schema."""

    logname = "dokastho"
    req_data = {
        "table": "schemas",
        "query": "SELECT * FROM tables WHERE owner = ?",
        "args": [logname]
    }
    req_hdrs = {
        'content_type': 'application/json'
    }
    
    post = c.get(req_data, req_hdrs)
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
    
    pw_hash = c.get(req_data, req_hdrs)
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
        
    user = c.get(req_data, req_hdrs)
    if len(user) == 0:
        assert(False)
    
    assert(user == [{'username': 'dokastho'}])
    pass
