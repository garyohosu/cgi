#!/usr/local/bin/python3
import sys
import uuid
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import _lib

def handler():
    method = os.environ.get('REQUEST_METHOD', 'GET')
    if method != 'GET':
        raise ValueError("Method not allowed")

    params = _lib.get_query_params()
    try:
        n = int(params.get('n', 1))
    except ValueError:
        raise ValueError("Invalid n")

    if n < 1 or n > 50:
        raise ValueError("n must be between 1 and 50")

    uuids = [str(uuid.uuid4()) for _ in range(n)]

    _lib.send_response(data={
        "uuids": uuids
    })

if __name__ == "__main__":
    _lib.main(handler)
