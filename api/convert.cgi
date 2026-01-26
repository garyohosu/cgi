#!/usr/local/bin/python3
import sys
import os
import math

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import _lib

def convert_temp(val, u_from, u_to):
    # Convert to Celsius first
    if u_from == 'c': c = val
    elif u_from == 'f': c = (val - 32) * 5/9
    elif u_from == 'k': c = val - 273.15
    else: raise ValueError(f"Unknown unit {u_from}")
    
    # Convert from Celsius
    if u_to == 'c': 
        return c, "C"
    elif u_to == 'f': 
        return c * 9/5 + 32, "(C * 9/5) + 32"
    elif u_to == 'k': 
        return c + 273.15, "C + 273.15"
    else: raise ValueError(f"Unknown unit {u_to}")

def convert_length(val, u_from, u_to):
    # Convert to meters first
    factors = {
        'mm': 0.001, 'cm': 0.01, 'm': 1.0, 'km': 1000.0,
        'inch': 0.0254, 'ft': 0.3048
    }
    if u_from not in factors: raise ValueError(f"Unknown unit {u_from}")
    m = val * factors[u_from]
    
    if u_to not in factors: raise ValueError(f"Unknown unit {u_to}")
    return m / factors[u_to], f"val * {factors[u_from]} / {factors[u_to]}"

def convert_pressure(val, u_from, u_to):
    # Convert to Pascal first
    factors = {
        'pa': 1.0, 'kpa': 1000.0, 'mpa': 1000000.0,
        'bar': 100000.0, 'psi': 6894.76
    }
    if u_from not in factors: raise ValueError(f"Unknown unit {u_from}")
    pa = val * factors[u_from]
    
    if u_to not in factors: raise ValueError(f"Unknown unit {u_to}")
    return pa / factors[u_to], f"val * {factors[u_from]} / {factors[u_to]}"

def handler():
    method = os.environ.get('REQUEST_METHOD', 'GET')
    if method != 'GET':
        raise ValueError("Method not allowed")

    params = _lib.get_query_params()
    kind = params.get('kind')
    try:
        val = float(params.get('value'))
    except (ValueError, TypeError):
        raise ValueError("Invalid value")
    if not math.isfinite(val):
        raise ValueError("Invalid value")
        
    u_from = params.get('from')
    u_to = params.get('to')
    
    if not kind or not u_from or not u_to:
        raise ValueError("Missing parameters")
        
    if kind == 'temp':
        res, formula = convert_temp(val, u_from.lower(), u_to.lower())
    elif kind == 'length':
        res, formula = convert_length(val, u_from.lower(), u_to.lower())
    elif kind == 'pressure':
        res, formula = convert_pressure(val, u_from.lower(), u_to.lower())
    else:
        raise ValueError("Unknown kind")

    _lib.send_response(data={
        "kind": kind,
        "input": {"value": val, "unit": u_from},
        "output": {"value": res, "unit": u_to},
        "formula": formula
    })

if __name__ == "__main__":
    _lib.main(handler)
