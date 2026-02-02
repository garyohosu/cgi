#!/usr/local/bin/python3
import sys
import os
import sqlite3
import json
import hashlib
import re

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import _lib

# Configuration
DATABASE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_data", "databases")
ALLOWED_ORIGINS = [
    "https://garyohosu.github.io",
    "http://localhost",
    "http://127.0.0.1"
]

# Maximum limits for safety
MAX_LIMIT = 1000
MAX_BATCH_SIZE = 100

def ensure_database_dir():
    """Ensure database directory exists"""
    if not os.path.exists(DATABASE_DIR):
        os.makedirs(DATABASE_DIR, mode=0o700, exist_ok=True)

def check_origin():
    """Check if request is from allowed origin"""
    origin = os.environ.get('HTTP_ORIGIN', '')
    referer = os.environ.get('HTTP_REFERER', '')
    
    # Check if origin or referer matches allowed origins
    for allowed in ALLOWED_ORIGINS:
        if origin.startswith(allowed) or referer.startswith(allowed):
            return True
    
    return False

def sanitize_identifier(name):
    """Sanitize table/column names to prevent SQL injection"""
    if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', name):
        raise ValueError(f"Invalid identifier: {name}")
    return name

def get_db_path(database_name):
    """Get database file path with validation"""
    # Sanitize database name
    db_name = sanitize_identifier(database_name)
    db_path = os.path.join(DATABASE_DIR, f"{db_name}.db")
    
    # Ensure path is within DATABASE_DIR (prevent path traversal)
    real_db_path = os.path.realpath(db_path)
    real_db_dir = os.path.realpath(DATABASE_DIR)
    
    if not real_db_path.startswith(real_db_dir):
        raise ValueError("Invalid database path")
    
    return db_path

def execute_select(conn, table, fields=None, where=None, order_by=None, limit=None):
    """Execute SELECT query"""
    table = sanitize_identifier(table)
    
    # Build SELECT clause
    if fields and isinstance(fields, list):
        field_list = ', '.join([sanitize_identifier(f) for f in fields])
    else:
        field_list = '*'
    
    query = f"SELECT {field_list} FROM {table}"
    params = []
    
    # Build WHERE clause
    if where and isinstance(where, dict):
        conditions = []
        for key, value in where.items():
            key = sanitize_identifier(key)
            conditions.append(f"{key} = ?")
            params.append(value)
        
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
    
    # Build ORDER BY clause
    if order_by and isinstance(order_by, list) and len(order_by) >= 1:
        col = sanitize_identifier(order_by[0])
        direction = order_by[1].upper() if len(order_by) > 1 else 'ASC'
        if direction not in ('ASC', 'DESC'):
            direction = 'ASC'
        query += f" ORDER BY {col} {direction}"
    
    # Build LIMIT clause
    if limit:
        limit = min(int(limit), MAX_LIMIT)
        query += f" LIMIT {limit}"
    
    cursor = conn.execute(query, params)
    columns = [desc[0] for desc in cursor.description]
    rows = [dict(zip(columns, row)) for row in cursor.fetchall()]
    
    return {"rows": rows, "count": len(rows)}

def execute_insert(conn, table, data):
    """Execute INSERT query"""
    table = sanitize_identifier(table)
    
    if not isinstance(data, dict) or not data:
        raise ValueError("Insert data must be a non-empty dictionary")
    
    columns = [sanitize_identifier(k) for k in data.keys()]
    placeholders = ', '.join(['?'] * len(columns))
    column_list = ', '.join(columns)
    
    query = f"INSERT INTO {table} ({column_list}) VALUES ({placeholders})"
    cursor = conn.execute(query, list(data.values()))
    
    return {"inserted_id": cursor.lastrowid, "affected_rows": cursor.rowcount}

def execute_update(conn, table, data, where):
    """Execute UPDATE query"""
    table = sanitize_identifier(table)
    
    if not isinstance(data, dict) or not data:
        raise ValueError("Update data must be a non-empty dictionary")
    
    if not where or not isinstance(where, dict):
        raise ValueError("WHERE clause is required for UPDATE")
    
    # Build SET clause
    set_clauses = []
    set_params = []
    for key, value in data.items():
        key = sanitize_identifier(key)
        set_clauses.append(f"{key} = ?")
        set_params.append(value)
    
    # Build WHERE clause
    where_clauses = []
    where_params = []
    for key, value in where.items():
        key = sanitize_identifier(key)
        where_clauses.append(f"{key} = ?")
        where_params.append(value)
    
    query = f"UPDATE {table} SET {', '.join(set_clauses)} WHERE {' AND '.join(where_clauses)}"
    cursor = conn.execute(query, set_params + where_params)
    
    return {"affected_rows": cursor.rowcount}

def execute_delete(conn, table, where):
    """Execute DELETE query"""
    table = sanitize_identifier(table)
    
    if not where or not isinstance(where, dict):
        raise ValueError("WHERE clause is required for DELETE")
    
    # Build WHERE clause
    where_clauses = []
    params = []
    for key, value in where.items():
        key = sanitize_identifier(key)
        where_clauses.append(f"{key} = ?")
        params.append(value)
    
    query = f"DELETE FROM {table} WHERE {' AND '.join(where_clauses)}"
    cursor = conn.execute(query, params)
    
    return {"affected_rows": cursor.rowcount}

def execute_count(conn, table, where=None):
    """Execute COUNT query"""
    table = sanitize_identifier(table)
    
    query = f"SELECT COUNT(*) as count FROM {table}"
    params = []
    
    if where and isinstance(where, dict):
        conditions = []
        for key, value in where.items():
            key = sanitize_identifier(key)
            conditions.append(f"{key} = ?")
            params.append(value)
        
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
    
    cursor = conn.execute(query, params)
    result = cursor.fetchone()
    
    return {"count": result[0]}

def execute_create_table(conn, table, schema):
    """Execute CREATE TABLE query"""
    table = sanitize_identifier(table)
    
    if not isinstance(schema, dict) or not schema:
        raise ValueError("Schema must be a non-empty dictionary")
    
    # Build column definitions
    columns = []
    for col_name, col_type in schema.items():
        col_name = sanitize_identifier(col_name)
        # Allow only safe SQL types
        col_type_upper = col_type.upper()
        allowed_types = ['INTEGER', 'TEXT', 'REAL', 'BLOB', 'NUMERIC', 'BOOLEAN', 'DATE', 'DATETIME']
        base_type = col_type_upper.split()[0]
        
        if base_type not in allowed_types:
            raise ValueError(f"Invalid column type: {col_type}")
        
        columns.append(f"{col_name} {col_type}")
    
    query = f"CREATE TABLE IF NOT EXISTS {table} ({', '.join(columns)})"
    conn.execute(query)
    
    return {"table_created": table}

def handler():
    method = os.environ.get('REQUEST_METHOD', 'GET')
    
    if method != 'POST':
        raise ValueError("Only POST method is allowed")
    
    # Check origin for security
    if not check_origin():
        raise ValueError("Unauthorized origin")
    
    ensure_database_dir()
    
    body = _lib.read_json_body()
    
    action = body.get('action', '')
    database = body.get('database', '')
    
    if not database:
        raise ValueError("Database name is required")
    
    # Get database path
    db_path = get_db_path(database)
    
    # Connect to database
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    
    try:
        if action == 'query':
            operation = body.get('operation', '')
            table = body.get('table', '')
            
            if not table:
                raise ValueError("Table name is required")
            
            result = None
            
            if operation == 'select':
                result = execute_select(
                    conn,
                    table,
                    fields=body.get('fields'),
                    where=body.get('where'),
                    order_by=body.get('order_by'),
                    limit=body.get('limit')
                )
            
            elif operation == 'insert':
                data = body.get('data')
                if not data:
                    raise ValueError("Data is required for insert")
                result = execute_insert(conn, table, data)
                conn.commit()
            
            elif operation == 'update':
                data = body.get('data')
                where = body.get('where')
                if not data or not where:
                    raise ValueError("Data and where are required for update")
                result = execute_update(conn, table, data, where)
                conn.commit()
            
            elif operation == 'delete':
                where = body.get('where')
                if not where:
                    raise ValueError("Where is required for delete")
                result = execute_delete(conn, table, where)
                conn.commit()
            
            elif operation == 'count':
                result = execute_count(conn, table, where=body.get('where'))
            
            elif operation == 'create_table':
                schema = body.get('schema')
                if not schema:
                    raise ValueError("Schema is required for create_table")
                result = execute_create_table(conn, table, schema)
                conn.commit()
            
            else:
                raise ValueError(f"Unknown operation: {operation}")
            
            _lib.send_response(data=result)
        
        else:
            raise ValueError(f"Unknown action: {action}")
    
    finally:
        conn.close()

if __name__ == "__main__":
    _lib.main(handler)
