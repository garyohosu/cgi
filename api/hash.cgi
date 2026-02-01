#!/usr/local/bin/python3
import sys
import os
import hashlib
import hmac

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import _lib

SUPPORTED_ALGORITHMS = ['md5', 'sha1', 'sha224', 'sha256', 'sha384', 'sha512']

def handler():
    method = os.environ.get('REQUEST_METHOD', 'GET')
    
    # Support both GET (for simple hashing) and POST (for HMAC with key)
    if method == 'GET':
        params = _lib.get_query_params()
        text = params.get('text', '')
        algorithm = params.get('algo', 'sha256').lower()
        mode = 'hash'
        key = None
        
    elif method == 'POST':
        body = _lib.read_json_body()
        text = body.get('text', '')
        algorithm = body.get('algo', 'sha256').lower()
        mode = body.get('mode', 'hash').lower()
        key = body.get('key', None)
    else:
        raise ValueError("Method not allowed")
    
    if not text:
        raise ValueError("text parameter required")
    
    if algorithm not in SUPPORTED_ALGORITHMS:
        raise ValueError(f"Unsupported algorithm. Supported: {', '.join(SUPPORTED_ALGORITHMS)}")
    
    # Encode text to bytes
    text_bytes = text.encode('utf-8')
    
    result = {
        "text": text,
        "algorithm": algorithm,
        "mode": mode
    }
    
    if mode == 'hash':
        # Simple hash
        hash_obj = hashlib.new(algorithm)
        hash_obj.update(text_bytes)
        hash_hex = hash_obj.hexdigest()
        
        result["hash"] = hash_hex
        result["length"] = len(hash_hex)
        
    elif mode == 'hmac':
        # HMAC with key
        if not key:
            raise ValueError("key required for HMAC mode")
        
        key_bytes = key.encode('utf-8')
        hmac_obj = hmac.new(key_bytes, text_bytes, algorithm)
        hmac_hex = hmac_obj.hexdigest()
        
        result["hmac"] = hmac_hex
        result["length"] = len(hmac_hex)
        result["key_length"] = len(key)
        
    else:
        raise ValueError("Invalid mode. Supported: hash, hmac")
    
    _lib.send_response(data=result)

if __name__ == "__main__":
    _lib.main(handler)
