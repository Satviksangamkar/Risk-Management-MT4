#!/usr/bin/env python3
"""
Test script for MT4 Calculator on port 5501
Tests both frontend and backend on the same port
"""
import requests
import os
import time

def test_integrated_app():
    """Test the integrated app on port 5501"""
    print("🚀 Testing MT4 Calculator on Port 5501")
    print("="*50)
    
    # Wait for server to start
    print("🔄 Waiting for server to start...")
    for i in range(15):
        try:
            response = requests.get('http://localhost:5501/health', timeout=2)
            if response.status_code == 200:
                print(f"✅ Server is ready on port 5501!")
                break
        except:
            print(f"   Waiting... ({i+1}/15)")
            time.sleep(1)
    else:
        print("❌ Server failed to start on port 5501")
        return False
    
    tests_passed = 0
    total_tests = 5
    
    # Test 1: Frontend accessibility
    print("\n🌐 Testing Frontend...")
    try:
        response = requests.get('http://localhost:5501/', timeout=5)
        if response.status_code == 200 and 'MT4 Calculator' in response.text:
            print("   ✅ Frontend loaded successfully")
            tests_passed += 1
        else:
            print(f"   ❌ Frontend failed: Status {response.status_code}")
    except Exception as e:
        print(f"   ❌ Frontend error: {e}")
    
    # Test 2: Static files
    print("\n📁 Testing Static Files...")
    try:
        css_response = requests.get('http://localhost:5501/static/styles.css', timeout=5)
        js_response = requests.get('http://localhost:5501/static/script.js', timeout=5)
        
        if css_response.status_code == 200 and js_response.status_code == 200:
            print("   ✅ Static files (CSS, JS) loaded successfully")
            tests_passed += 1
        else:
            print(f"   ❌ Static files failed: CSS {css_response.status_code}, JS {js_response.status_code}")
    except Exception as e:
        print(f"   ❌ Static files error: {e}")
    
    # Test 3: API Health
    print("\n🔍 Testing API Health...")
    try:
        response = requests.get('http://localhost:5501/api/v1/mt4/health', timeout=5)
        if response.status_code == 200:
            print("   ✅ API health check passed")
            tests_passed += 1
        else:
            print(f"   ❌ API health failed: Status {response.status_code}")
    except Exception as e:
        print(f"   ❌ API health error: {e}")
    
    # Test 4: Risk Calculator
    print("\n💰 Testing Risk Calculator...")
    try:
        data = {
            'entry_price': 1.2500,
            'stop_loss': 1.2450,
            'take_profit': 1.2600,
            'trade_type': 'buy',
            'account_balance': 10000.0,
            'risk_percentage': 2.0
        }
        
        response = requests.post('http://localhost:5501/api/v1/mt4/risk-calculator', json=data, timeout=10)
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Risk calculator working - R-Multiple: {result['data']['risk_metrics']['r_multiple']:.2f}")
            tests_passed += 1
        else:
            print(f"   ❌ Risk calculator failed: Status {response.status_code}")
    except Exception as e:
        print(f"   ❌ Risk calculator error: {e}")
    
    # Test 5: File Analysis
    print("\n📊 Testing File Analysis...")
    file_path = os.path.abspath('10.htm')
    if os.path.exists(file_path):
        try:
            with open(file_path, 'rb') as f:
                files = {'file': (os.path.basename(file_path), f, 'text/html')}
                params = {'calculate_r_multiple': True, 'include_open_trades': True}
                
                response = requests.post(
                    'http://localhost:5501/api/v1/mt4/analyze/file',
                    files=files,
                    params=params,
                    timeout=30
                )
            
            if response.status_code == 200:
                result = response.json()
                print(f"   ✅ File analysis working - {result.get('total_trades')} trades processed")
                tests_passed += 1
            else:
                print(f"   ❌ File analysis failed: Status {response.status_code}")
        except Exception as e:
            print(f"   ❌ File analysis error: {e}")
    else:
        print(f"   ⚠️ Test file not found: {file_path}")
    
    # Results
    print("\n" + "="*50)
    print("🎯 TEST RESULTS")
    print("="*50)
    print(f"Tests passed: {tests_passed}/{total_tests}")
    
    if tests_passed == total_tests:
        print("\n🎉 ALL TESTS PASSED!")
        print("✅ Frontend and Backend integrated successfully")
        print("✅ All functionality working on port 5501")
        print("\n🌐 Access your MT4 Calculator at:")
        print("   http://localhost:5501")
        print("\n📋 Features ready:")
        print("   - File upload and analysis")
        print("   - Risk calculator")
        print("   - Modern responsive interface")
        print("   - Real-time progress tracking")
    else:
        print(f"\n⚠️  {total_tests - tests_passed} test(s) failed")
        print("Check the server startup and try again.")
    
    return tests_passed == total_tests

if __name__ == "__main__":
    test_integrated_app()
