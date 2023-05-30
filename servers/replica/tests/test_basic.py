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
