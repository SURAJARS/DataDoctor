#!/usr/bin/env python3
"""
Test script to verify CSV attachment in email functionality
Tests the complete flow: upload -> analyze -> send email with CSV
"""

import requests
import json
import time
import os
from pathlib import Path

BASE_URL = "http://localhost:8000"
TEST_EMAIL = "surajars24@gmail.com"
TEST_FILE = Path("sample_data.csv")

def test_upload_and_analyze():
    """Test 1: Upload dataset and run analysis"""
    print("\n" + "="*60)
    print("TEST 1: UPLOAD & ANALYZE")
    print("="*60)
    
    if not TEST_FILE.exists():
        print(f"❌ Test file not found: {TEST_FILE}")
        return None
    
    print(f"📁 Uploading: {TEST_FILE}")
    with open(TEST_FILE, 'rb') as f:
        files = {'file': f}
        data = {'target_column': 'default'}
        response = requests.post(
            f"{BASE_URL}/api/analyze",
            files=files,
            data=data
        )
    
    if response.status_code != 200:
        print(f"❌ Upload Failed: {response.status_code}")
        print(f"   Response: {response.text}")
        return None
    
    result = response.json()
    analysis_id = result.get('analysis_id')
    print(f"✓ Analysis created: {analysis_id}")
    print(f"  Dataset: {result['summary'].get('critical_issues')} critical issues")
    
    # Wait for analysis to complete
    time.sleep(2)
    
    return analysis_id

def test_send_email_with_csv(analysis_id):
    """Test 2: Send email with CSV attachment"""
    print("\n" + "="*60)
    print("TEST 2: SEND EMAIL WITH CSV ATTACHMENT")
    print("="*60)
    
    url = f"{BASE_URL}/api/report/send-email"
    params = {
        'email': TEST_EMAIL,
        'analysis_id': analysis_id,
        'include_csv': True
    }
    
    print(f"📧 Sending email to: {TEST_EMAIL}")
    print(f"   Analysis ID: {analysis_id}")
    print(f"   Include CSV: True")
    
    response = requests.post(url, params=params)
    
    if response.status_code != 200:
        print(f"❌ Email send failed: {response.status_code}")
        print(f"   Response: {response.text}")
        return False
    
    result = response.json()
    print(f"✓ Email sent successfully")
    print(f"  Status: {result.get('status')}")
    print(f"  CSV Included: {result.get('csv_included')}")
    print(f"  Message: {result.get('message')}")
    
    return result.get('csv_included', False)

def test_no_csv_attachment(analysis_id):
    """Test 3: Send email WITHOUT CSV attachment"""
    print("\n" + "="*60)
    print("TEST 3: SEND EMAIL WITHOUT CSV (Testing checkbox=false)")
    print("="*60)
    
    url = f"{BASE_URL}/api/report/send-email"
    params = {
        'email': TEST_EMAIL,
        'analysis_id': analysis_id,
        'include_csv': False
    }
    
    print(f"📧 Sending email (no CSV) to: {TEST_EMAIL}")
    print(f"   Include CSV: False")
    
    response = requests.post(url, params=params)
    
    if response.status_code != 200:
        print(f"❌ Email send failed: {response.status_code}")
        return False
    
    result = response.json()
    print(f"✓ Email sent successfully")
    print(f"  CSV Included: {result.get('csv_included')}")
    
    return result.get('csv_included', False)

def main():
    print("\n" + "🔍 " * 20)
    print("DATA DOCTOR - CSV EMAIL ATTACHMENT TEST")
    print("🔍 " * 20)
    
    # Check backend is running
    try:
        response = requests.get(f"{BASE_URL}/")
        print(f"\n✓ Backend running on {BASE_URL}")
    except:
        print(f"\n❌ Cannot connect to backend at {BASE_URL}")
        print("   Make sure backend is running: python backend/main.py")
        return
    
    # Test 1: Upload & Analyze
    analysis_id = test_upload_and_analyze()
    if not analysis_id:
        print("\n❌ Cannot proceed without analysis ID")
        return
    
    # Test 2: Send with CSV
    csv_attached_1 = test_send_email_with_csv(analysis_id)
    
    # Test 3: Send without CSV
    csv_not_attached = not test_no_csv_attachment(analysis_id)
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    tests_passed = 0
    tests_total = 2
    
    if csv_attached_1:
        print("✓ TEST 1 PASSED: CSV attached when include_csv=True")
        tests_passed += 1
    else:
        print("❌ TEST 1 FAILED: CSV not attached when include_csv=True")
    
    if csv_not_attached:
        print("✓ TEST 2 PASSED: CSV not attached when include_csv=False")
        tests_passed += 1
    else:
        print("❌ TEST 2 FAILED: CSV was attached when include_csv=False")
    
    print(f"\n{'='*60}")
    print(f"RESULT: {tests_passed}/{tests_total} tests passed")
    print(f"{'='*60}")
    
    print("\n📧 CHECK YOUR EMAIL:")
    print(f"   Inbox: {TEST_EMAIL}")
    print(f"   Subject: 'DATA DOCTOR Analysis Report'")
    print(f"   Expected attachments:")
    print(f"      ✓ PDF report file")
    if csv_attached_1:
        print(f"      ✓ Cleaned CSV dataset (with ALL rows, not just 100)")
    else:
        print(f"      ✗ No CSV in first email")
    if csv_not_attached:
        print(f"      ✗ No CSV in second email (sent with include_csv=False)")
    
    print("\n✅ END-TO-END TEST COMPLETE!")

if __name__ == "__main__":
    main()
