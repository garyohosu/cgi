#!/usr/local/bin/python3
import sys
import os
import re

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import _lib

def validate(schema, data, path="$"):
    errors = []
    
    # Type check
    schema_type = schema.get("type")
    if schema_type:
        valid_type = True
        if schema_type == "object":
            if not isinstance(data, dict): valid_type = False
        elif schema_type == "array":
            if not isinstance(data, list): valid_type = False
        elif schema_type == "string":
            if not isinstance(data, str): valid_type = False
        elif schema_type == "integer":
            if not isinstance(data, int) or isinstance(data, bool): valid_type = False
        elif schema_type == "number":
            if not isinstance(data, (int, float)) or isinstance(data, bool): valid_type = False
        elif schema_type == "boolean":
            if not isinstance(data, bool): valid_type = False
        elif schema_type == "null":
            if data is not None: valid_type = False
            
        if not valid_type:
            errors.append({"path": path, "message": f"expected {schema_type} but got {type(data).__name__}"})
            return errors # Stop further validation if type mismatches

    # Object validation
    if schema_type == "object":
        required = schema.get("required", [])
        for req in required:
            if req not in data:
                errors.append({"path": path, "message": f"missing required property '{req}'"})
        
        properties = schema.get("properties", {})
        additional_properties = schema.get("additionalProperties", True) 
        
        for key, value in data.items():
            if key in properties:
                errors.extend(validate(properties[key], value, f"{path}.{key}"))
            elif additional_properties is False:
                 errors.append({"path": path, "message": f"additional property '{key}' not allowed"})

    # String validation
    if schema_type == "string":
        if "minLength" in schema and len(data) < schema["minLength"]:
            errors.append({"path": path, "message": f"length {len(data)} < minLength {schema['minLength']}"})
        if "maxLength" in schema and len(data) > schema["maxLength"]:
            errors.append({"path": path, "message": f"length {len(data)} > maxLength {schema['maxLength']}"})
        if "pattern" in schema:
            try:
                if not re.search(schema["pattern"], data):
                    errors.append({"path": path, "message": f"does not match pattern '{schema['pattern']}'"})
            except re.error:
                errors.append({"path": path, "message": f"invalid regex pattern '{schema['pattern']}'"})

    # Number/Integer validation
    if schema_type in ("integer", "number"):
        if "minimum" in schema and data < schema["minimum"]:
            errors.append({"path": path, "message": f"value {data} < minimum {schema['minimum']}"})
        if "maximum" in schema and data > schema["maximum"]:
            errors.append({"path": path, "message": f"value {data} > maximum {schema['maximum']}"})

    # Array validation
    if schema_type == "array":
        if "minItems" in schema and len(data) < schema["minItems"]:
            errors.append({"path": path, "message": f"items {len(data)} < minItems {schema['minItems']}"})
        if "maxItems" in schema and len(data) > schema["maxItems"]:
            errors.append({"path": path, "message": f"items {len(data)} > maxItems {schema['maxItems']}"})
        
        items_schema = schema.get("items")
        if items_schema:
            for i, item in enumerate(data):
                errors.extend(validate(items_schema, item, f"{path}[{i}]"))

    return errors

def handler():
    method = os.environ.get('REQUEST_METHOD', 'GET')
    if method != 'POST':
        raise ValueError("Method not allowed")

    body = _lib.read_json_body()
    
    if "schema" not in body or "data" not in body:
        raise ValueError("Missing schema or data")

    schema = body["schema"]
    data = body["data"]

    if not isinstance(schema, dict):
        raise ValueError("Invalid schema")
    
    errors = validate(schema, data)
    
    _lib.send_response(data={
        "valid": len(errors) == 0,
        "errors": errors
    })

if __name__ == "__main__":
    _lib.main(handler)
