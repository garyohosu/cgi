#!/usr/local/bin/python3
import sys
import datetime
import os

# Ensure we can import _lib
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import _lib

def handler():
    method = os.environ.get('REQUEST_METHOD', 'GET')
    if method != 'GET':
        # Should strictly be 405, but spec says "GET only" and generic error handling
        # reusing ValueError for simplicity as per _lib adapter
        raise ValueError("Method not allowed")

    params = _lib.get_query_params()
    tz_param = params.get('tz', 'jst').lower()

    if tz_param not in ('jst', 'utc'):
        raise ValueError("Invalid timezone")

    now_utc = datetime.datetime.now(datetime.timezone.utc)
    
    if tz_param == 'jst':
        tz = datetime.timezone(datetime.timedelta(hours=9))
        now = now_utc.astimezone(tz)
        tz_str = "JST"
    else:
        now = now_utc
        tz_str = "UTC"

    _lib.send_response(data={
        "iso": now.isoformat(),
        "epoch": now.timestamp(),
        "tz": tz_str
    })

if __name__ == "__main__":
    _lib.main(handler)
