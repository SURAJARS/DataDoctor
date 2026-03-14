#!/usr/bin/env python
"""Simple endpoint test"""

import requests
import json
import time

# Wait for backend
time.sleep(1)

# 1. Simple health check
print("Health Check:")
try:
    r = requests.get('http://localhost:8000/', timeout=5)
    print(f"Status: {r.status_code}")
except Exception as e:
    print(f"Failed: {e}")

print("\nAnalyze Endpoint:")
try:
    with open('sample_data.csv', 'rb') as f:
        files = {'file': ('sample_data.csv', f, 'text/csv')}
        r = requests.post('http://localhost:8000/api/analyze', files=files, timeout=15)
    print(f"Status: {r.status_code}")
    if r.status_code == 200:
        data = r.json()
        analysis_id = data.get('analysis_id', 'N/A')
        print(f"Analysis ID: {analysis_id}")
    else:
        print(f"Error: {r.text[:200]}")
except Exception as e:
    print(f"Error: {e}")
