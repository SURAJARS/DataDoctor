#!/usr/bin/env python
"""Quick test of endpoints"""

import requests
import json

print("Testing Auto-Fix Endpoint with new Pydantic model...")
try:
    response = requests.post(
        'http://localhost:8000/api/auto-fix',
        json={'analysis_id': 'test123'},
        timeout=5
    )
    print(f"Status: {response.status_code}")
    if response.status_code != 200:
        print(f"Error: {response.text}")
    else:
        print(f"Response: {response.json().get('status', 'N/A')}")
except Exception as e:
    print(f"Error: {str(e)[:100]}")

print("\nTesting Drift Detection Endpoint...")
try:
    response = requests.post(
        'http://localhost:8000/api/drift-detection',
        json={'analysis_id': 'test123'},
        timeout=5
    )
    print(f"Status: {response.status_code}")
    if response.status_code != 200:
        print(f"Error: {response.text}")
    else:
        print(f"Response: {response.json().get('status', 'N/A')}")
except Exception as e:
    print(f"Error: {str(e)[:100]}")

print("\nTesting Pipeline Endpoint...")
try:
    response = requests.get(
        'http://localhost:8000/api/pipeline/test123',
        timeout=5
    )
    print(f"Status: {response.status_code}")
    if response.status_code != 200:
        print(f"Error: {response.text}")
    else:
        data = response.json()
        code_len = len(data.get('pipeline_code', ''))
        print(f"Response: Pipeline code generated ({code_len} chars)")
except Exception as e:
    print(f"Error: {str(e)[:100]}")

print("\nAll tests completed!")
