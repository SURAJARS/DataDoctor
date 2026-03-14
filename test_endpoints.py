#!/usr/bin/env python
"""Test all backend endpoints"""

import requests
import sys
import time

time.sleep(3)  # Wait for backend to start

try:
    # 1. Upload and analyze a sample dataset
    print('1. Uploading sample dataset...')
    with open('sample_data.csv', 'rb') as f:
        files = {'file': f}
        response = requests.post('http://localhost:8000/api/analyze', files=files, timeout=10)
    
    if response.status_code != 200:
        print(f'Analyze failed: {response.status_code}')
        print(response.text)
        sys.exit(1)
    
    data = response.json()
    analysis_id = data.get('analysis_id', 'latest')
    print(f'Analysis ID: {analysis_id}')
    print()
    
    # 2. Test Risk Score 
    print('2. Testing Risk Score endpoint...')
    response = requests.get(f'http://localhost:8000/api/risk-score/{analysis_id}', timeout=10)
    if response.status_code == 200:
        result = response.json()
        print(f'   Status: {response.status_code}')
        print(f'   Risk Score: {result.get("risk_score", "N/A")}')
        print(f'   Risk Level: {result.get("risk_level", "Unknown")}')
    else:
        print(f'   FAILED: {response.status_code}')
        print(f'   Error: {response.text}')
    print()
    
    # 3. Test Auto-Fix
    print('3. Testing Auto-Fix endpoint...')
    response = requests.post('http://localhost:8000/api/auto-fix', json={'analysis_id': analysis_id}, timeout=10)
    if response.status_code == 200:
        result = response.json()
        print(f'   Status: {response.status_code}')
        print(f'   Response Status: {result.get("status", "unknown")}')
    else:
        print(f'   FAILED: {response.status_code}')
        print(f'   Error: {response.text}')
    print()
    
    # 4. Test Drift Detection
    print('4. Testing Drift Detection endpoint...')
    response = requests.post('http://localhost:8000/api/drift-detection', json={'analysis_id': analysis_id}, timeout=10)
    if response.status_code == 200:
        result = response.json()
        print(f'   Status: {response.status_code}')
        print(f'   Response Status: {result.get("status", "unknown")}')
    else:
        print(f'   FAILED: {response.status_code}')
        print(f'   Error: {response.text}')
    print()
    
    # 5. Test Pipeline Generation
    print('5. Testing Pipeline Generation endpoint...')
    response = requests.get(f'http://localhost:8000/api/pipeline/{analysis_id}', timeout=10)
    if response.status_code == 200:
        result = response.json()
        print(f'   Status: {response.status_code}')
        print(f'   Response Status: {result.get("status", "unknown")}')
        code = result.get('pipeline_code', '')
        print(f'   Code length: {len(code)} characters')
        if len(code) > 0:
            print(f'   Code sample: {code[:80]}...')
    else:
        print(f'   FAILED: {response.status_code}')
        print(f'   Error: {response.text}')
    print()
    
    print('All endpoint tests completed!')
    
except Exception as e:
    print(f'Error: {e}')
    import traceback
    traceback.print_exc()
