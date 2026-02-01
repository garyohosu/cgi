#!/usr/local/bin/python3
import sys
import os
import random
import string

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import _lib

def handler():
    method = os.environ.get('REQUEST_METHOD', 'GET')
    if method != 'GET':
        raise ValueError("Method not allowed")

    params = _lib.get_query_params()
    kind = params.get('kind', 'number').lower()
    
    result = {}
    
    if kind == 'number':
        # Random number generation
        try:
            min_val = int(params.get('min', 1))
            max_val = int(params.get('max', 100))
            count = int(params.get('count', 1))
        except ValueError:
            raise ValueError("Invalid parameters")
        
        if count < 1 or count > 100:
            raise ValueError("count must be between 1 and 100")
        
        if min_val >= max_val:
            raise ValueError("min must be less than max")
        
        numbers = [random.randint(min_val, max_val) for _ in range(count)]
        result = {
            "type": "number",
            "values": numbers,
            "min": min_val,
            "max": max_val,
            "count": count
        }
    
    elif kind == 'choice':
        # Random choice from list
        items_str = params.get('items', '')
        if not items_str:
            raise ValueError("items parameter required")
        
        items = [item.strip() for item in items_str.split(',') if item.strip()]
        if len(items) < 2:
            raise ValueError("At least 2 items required")
        
        try:
            count = int(params.get('count', 1))
        except ValueError:
            raise ValueError("Invalid count")
        
        if count < 1 or count > len(items):
            raise ValueError(f"count must be between 1 and {len(items)}")
        
        # unique=true for sampling without replacement
        unique = params.get('unique', 'false').lower() == 'true'
        
        if unique:
            selected = random.sample(items, count)
        else:
            selected = [random.choice(items) for _ in range(count)]
        
        result = {
            "type": "choice",
            "selected": selected,
            "items": items,
            "count": count,
            "unique": unique
        }
    
    elif kind == 'string':
        # Random string generation
        try:
            length = int(params.get('length', 16))
        except ValueError:
            raise ValueError("Invalid length")
        
        if length < 1 or length > 256:
            raise ValueError("length must be between 1 and 256")
        
        charset_param = params.get('charset', 'alphanumeric').lower()
        
        if charset_param == 'alphanumeric':
            charset = string.ascii_letters + string.digits
        elif charset_param == 'alpha':
            charset = string.ascii_letters
        elif charset_param == 'numeric':
            charset = string.digits
        elif charset_param == 'hex':
            charset = string.hexdigits.lower()
        elif charset_param == 'alphanumsym':
            charset = string.ascii_letters + string.digits + "!@#$%^&*"
        else:
            raise ValueError("Invalid charset")
        
        random_string = ''.join(random.choice(charset) for _ in range(length))
        
        result = {
            "type": "string",
            "value": random_string,
            "length": length,
            "charset": charset_param
        }
    
    elif kind == 'dice':
        # Dice roll simulation
        try:
            sides = int(params.get('sides', 6))
            count = int(params.get('count', 1))
        except ValueError:
            raise ValueError("Invalid parameters")
        
        if sides < 2 or sides > 100:
            raise ValueError("sides must be between 2 and 100")
        
        if count < 1 or count > 100:
            raise ValueError("count must be between 1 and 100")
        
        rolls = [random.randint(1, sides) for _ in range(count)]
        total = sum(rolls)
        
        result = {
            "type": "dice",
            "rolls": rolls,
            "total": total,
            "sides": sides,
            "count": count
        }
    
    elif kind == 'coin':
        # Coin flip
        try:
            count = int(params.get('count', 1))
        except ValueError:
            raise ValueError("Invalid count")
        
        if count < 1 or count > 100:
            raise ValueError("count must be between 1 and 100")
        
        flips = [random.choice(['heads', 'tails']) for _ in range(count)]
        heads = flips.count('heads')
        tails = flips.count('tails')
        
        result = {
            "type": "coin",
            "flips": flips,
            "heads": heads,
            "tails": tails,
            "count": count
        }
    
    else:
        raise ValueError("Invalid kind parameter")
    
    _lib.send_response(data=result)

if __name__ == "__main__":
    _lib.main(handler)
