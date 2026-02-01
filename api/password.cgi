#!/usr/local/bin/python3
import sys
import os
import secrets
import string

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import _lib

def handler():
    method = os.environ.get('REQUEST_METHOD', 'GET')
    if method != 'GET':
        raise ValueError("Method not allowed")

    params = _lib.get_query_params()
    
    # Password length (default: 16)
    try:
        length = int(params.get('length', 16))
    except ValueError:
        raise ValueError("Invalid length")
    
    if length < 8 or length > 128:
        raise ValueError("length must be between 8 and 128")
    
    # Number of passwords to generate (default: 1)
    try:
        count = int(params.get('count', 1))
    except ValueError:
        raise ValueError("Invalid count")
    
    if count < 1 or count > 20:
        raise ValueError("count must be between 1 and 20")
    
    # Complexity level
    complexity = params.get('complexity', 'medium').lower()
    
    if complexity == 'low':
        # Only letters and numbers
        charset = string.ascii_letters + string.digits
        requirements = {
            "uppercase": True,
            "lowercase": True,
            "digits": True,
            "symbols": False
        }
    elif complexity == 'medium':
        # Letters, numbers, and basic symbols
        charset = string.ascii_letters + string.digits + "!@#$%^&*"
        requirements = {
            "uppercase": True,
            "lowercase": True,
            "digits": True,
            "symbols": True
        }
    elif complexity == 'high':
        # All printable characters
        charset = string.ascii_letters + string.digits + "!@#$%^&*()-_=+[]{}|;:,.<>?/"
        requirements = {
            "uppercase": True,
            "lowercase": True,
            "digits": True,
            "symbols": True
        }
    else:
        raise ValueError("Invalid complexity level")
    
    # Generate passwords
    passwords = []
    for _ in range(count):
        while True:
            # Use secrets for cryptographically strong random password
            password = ''.join(secrets.choice(charset) for _ in range(length))
            
            # Verify password meets requirements
            has_upper = any(c.isupper() for c in password)
            has_lower = any(c.islower() for c in password)
            has_digit = any(c.isdigit() for c in password)
            has_symbol = any(c in "!@#$%^&*()-_=+[]{}|;:,.<>?/" for c in password)
            
            if requirements["uppercase"] and not has_upper:
                continue
            if requirements["lowercase"] and not has_lower:
                continue
            if requirements["digits"] and not has_digit:
                continue
            if requirements["symbols"] and not has_symbol:
                continue
            
            break
        
        passwords.append(password)
    
    # Calculate strength estimate
    charset_size = len(charset)
    entropy_bits = length * (charset_size.bit_length() - 1)
    
    if entropy_bits < 40:
        strength = "weak"
    elif entropy_bits < 60:
        strength = "fair"
    elif entropy_bits < 80:
        strength = "good"
    elif entropy_bits < 100:
        strength = "strong"
    else:
        strength = "very strong"
    
    _lib.send_response(data={
        "passwords": passwords,
        "length": length,
        "count": count,
        "complexity": complexity,
        "charset_size": charset_size,
        "entropy_bits": entropy_bits,
        "strength": strength
    })

if __name__ == "__main__":
    _lib.main(handler)
