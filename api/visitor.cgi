#!/usr/local/bin/python3
import sys
import os
import datetime
import json
import hashlib
import glob

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import _lib

# Data storage directory (relative to script location)
DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_data", "visitors")

# Allowed origins for CORS
ALLOWED_ORIGINS = [
    "https://garyohosu.github.io",
    "http://localhost",
    "http://127.0.0.1"
]

# Simple country/city data for demonstration
# In production, use GeoIP database or external API
DEMO_LOCATIONS = {
    "default": {"country": "Unknown", "city": "Unknown", "lat": 35.6762, "lon": 139.6503},
    "jp": {"country": "Japan", "city": "Tokyo", "lat": 35.6762, "lon": 139.6503},
    "us": {"country": "USA", "city": "New York", "lat": 40.7128, "lon": -74.0060},
    "uk": {"country": "United Kingdom", "city": "London", "lat": 51.5074, "lon": -0.1278},
    "de": {"country": "Germany", "city": "Berlin", "lat": 52.5200, "lon": 13.4050},
    "fr": {"country": "France", "city": "Paris", "lat": 48.8566, "lon": 2.3522},
    "cn": {"country": "China", "city": "Beijing", "lat": 39.9042, "lon": 116.4074},
    "kr": {"country": "South Korea", "city": "Seoul", "lat": 37.5665, "lon": 126.9780},
}

def ensure_data_dir():
    """Ensure data directory exists"""
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR, exist_ok=True)

def check_origin():
    """Check if request is from allowed origin"""
    origin = os.environ.get('HTTP_ORIGIN', '')
    referer = os.environ.get('HTTP_REFERER', '')
    
    # Check if origin or referer matches allowed origins
    for allowed in ALLOWED_ORIGINS:
        if origin.startswith(allowed) or referer.startswith(allowed):
            return True
    
    return False

def get_client_ip():
    """Get client IP address"""
    # Try various headers set by proxies/load balancers
    ip = os.environ.get('HTTP_X_FORWARDED_FOR', '').split(',')[0].strip()
    if not ip:
        ip = os.environ.get('HTTP_X_REAL_IP', '')
    if not ip:
        ip = os.environ.get('REMOTE_ADDR', '0.0.0.0')
    return ip

def hash_ip(ip):
    """Hash IP address for privacy"""
    return hashlib.sha256(ip.encode()).hexdigest()[:16]

def guess_location(ip):
    """Simple location guessing based on IP
    In production, use GeoIP2 database or external API like ip-api.com
    """
    # For demo, just cycle through locations based on IP hash
    ip_hash = int(hashlib.md5(ip.encode()).hexdigest()[:8], 16)
    location_keys = list(DEMO_LOCATIONS.keys())
    location_key = location_keys[ip_hash % len(location_keys)]
    return DEMO_LOCATIONS[location_key].copy()

def save_visitor(data):
    """Save visitor data to JSONL file"""
    ensure_data_dir()
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    file_path = os.path.join(DATA_DIR, f"{today}.jsonl")
    
    with open(file_path, 'a', encoding='utf-8') as f:
        f.write(json.dumps(data, ensure_ascii=False) + '\n')

def load_visitors(days=1):
    """Load visitor data from recent days"""
    ensure_data_dir()
    visitors = []
    
    # Get date range
    end_date = datetime.datetime.now()
    start_date = end_date - datetime.timedelta(days=days)
    
    # Load files from date range
    for i in range(days + 1):
        date = start_date + datetime.timedelta(days=i)
        date_str = date.strftime("%Y-%m-%d")
        file_path = os.path.join(DATA_DIR, f"{date_str}.jsonl")
        
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line:
                        try:
                            visitors.append(json.loads(line))
                        except json.JSONDecodeError:
                            continue
    
    return visitors

def get_stats():
    """Calculate visitor statistics"""
    # Load recent visitors (last 7 days)
    all_visitors = load_visitors(days=7)
    
    # Today's visitors
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    today_visitors = [v for v in all_visitors if v['timestamp'].startswith(today)]
    
    # Online now (last 5 minutes)
    now = datetime.datetime.now(datetime.timezone.utc)
    five_min_ago = now - datetime.timedelta(minutes=5)
    online_visitors = [
        v for v in all_visitors 
        if datetime.datetime.fromisoformat(v['timestamp'].replace('Z', '+00:00')) > five_min_ago
    ]
    
    # Recent visitors for map (last 100)
    recent_visitors = sorted(all_visitors, key=lambda x: x['timestamp'], reverse=True)[:100]
    recent_for_map = [
        {
            "country": v["location"]["country"],
            "city": v["location"]["city"],
            "lat": v["location"]["lat"],
            "lon": v["location"]["lon"],
            "timestamp": v["timestamp"]
        }
        for v in recent_visitors
    ]
    
    # Hourly stats for today
    hourly_counts = {}
    for v in today_visitors:
        hour = v['timestamp'][11:13]  # Extract HH from ISO format
        hourly_counts[hour] = hourly_counts.get(hour, 0) + 1
    
    hourly_stats = [{"hour": f"{h:02d}:00", "count": hourly_counts.get(f"{h:02d}", 0)} for h in range(24)]
    
    # Top countries
    country_counts = {}
    for v in all_visitors:
        country = v["location"]["country"]
        country_counts[country] = country_counts.get(country, 0) + 1
    
    top_countries = sorted(
        [{"country": k, "count": v} for k, v in country_counts.items()],
        key=lambda x: x["count"],
        reverse=True
    )[:10]
    
    return {
        "total_visits": len(all_visitors),
        "today_visits": len(today_visitors),
        "online_now": len(online_visitors),
        "recent_visitors": recent_for_map,
        "hourly_stats": hourly_stats,
        "top_countries": top_countries
    }

def handler():
    method = os.environ.get('REQUEST_METHOD', 'GET')
    
    # Check origin for security
    if not check_origin():
        raise ValueError("Unauthorized origin")
    
    if method == 'POST':
        # Record a visit
        body = _lib.read_json_body()
        action = body.get('action', '')
        
        if action != 'visit':
            raise ValueError("Invalid action")
        
        # Get client IP and location
        ip = get_client_ip()
        ip_hash = hash_ip(ip)
        location = guess_location(ip)
        
        # Create visitor record
        visitor_data = {
            "id": ip_hash,
            "location": location,
            "page": body.get('page', '/'),
            "referrer": body.get('referrer', ''),
            "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "user_agent": os.environ.get('HTTP_USER_AGENT', '')[:200]  # Truncate for safety
        }
        
        # Save to storage
        save_visitor(visitor_data)
        
        _lib.send_response(data={
            "success": True,
            "visitor_id": ip_hash,
            "location": location,
            "timestamp": visitor_data['timestamp']
        })
    
    elif method == 'GET':
        # Get statistics
        params = _lib.get_query_params()
        action = params.get('action', 'stats')
        
        if action != 'stats':
            raise ValueError("Invalid action")
        
        stats = get_stats()
        _lib.send_response(data=stats)
    
    else:
        raise ValueError("Method not allowed")

if __name__ == "__main__":
    _lib.main(handler)
