#!/usr/bin/env python3
"""
Test script for FastAPI server with 10.htm file
"""

import requests
import json
import time
from pathlib import Path

def test_server_health():
    """Test if server is running"""
    try:
        response = requests.get("http://localhost:8000/health", timeout=10)
        print(f"Health check: {response.status_code}")
        if response.status_code == 200:
            print(f"Server response: {response.json()}")
            return True
    except Exception as e:
        print(f"Health check failed: {e}")
    return False

def test_with_htm_file():
    """Test the server with 10.htm file"""
    try:
        # First test with file path endpoint
        htm_path = str(Path("10.htm").resolve())
        print(f"Testing with file path: {htm_path}")
        
        response = requests.post(
            "http://localhost:8000/api/v1/mt4/analyze/path",
            params={
                "file_path": htm_path,
                "calculate_r_multiple": True,
                "include_open_trades": True
            },
            timeout=30
        )
        
        print(f"Path analysis response: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print("✅ Analysis successful!")
            print(f"\n📊 Full Response Structure:")
            print(json.dumps(result, indent=2, default=str))
            
            # Extract and display all the calculations
            data = result.get('data', {})
            account_info = data.get('account_info', {})
            financial_summary = data.get('financial_summary', {})
            calculated_metrics = data.get('calculated_metrics', {})
            r_multiple_stats = data.get('r_multiple_statistics', {})
            
            print(f"\n🏦 Account Info:")
            print(f"  Account: {account_info.get('account_number', 'N/A')}")
            print(f"  Name: {account_info.get('account_name', 'N/A')}")
            print(f"  Currency: {account_info.get('currency', 'N/A')}")
            print(f"  Leverage: {account_info.get('leverage', 'N/A')}")
            
            print(f"\n💰 Financial Summary:")
            print(f"  Balance: ${financial_summary.get('balance', 0):,.2f}")
            print(f"  Equity: ${financial_summary.get('equity', 0):,.2f}")
            print(f"  Closed P/L: ${financial_summary.get('closed_trade_pnl', 0):,.2f}")
            print(f"  Floating P/L: ${financial_summary.get('floating_pnl', 0):,.2f}")
            print(f"  Margin: ${financial_summary.get('margin', 0):,.2f}")
            print(f"  Free Margin: ${financial_summary.get('free_margin', 0):,.2f}")
            
            print(f"\n📈 Calculated Metrics ({len([k for k,v in calculated_metrics.items() if v is not None])} metrics):")
            for key, value in calculated_metrics.items():
                if isinstance(value, float):
                    if 'percentage' in key or 'rate' in key:
                        print(f"  {key.replace('_', ' ').title()}: {value:.2f}%")
                    else:
                        print(f"  {key.replace('_', ' ').title()}: {value:.4f}")
                else:
                    print(f"  {key.replace('_', ' ').title()}: {value}")
                    
            print(f"\n🎯 R-Multiple Statistics:")
            for key, value in r_multiple_stats.items():
                if isinstance(value, dict):
                    print(f"  {key.replace('_', ' ').title()}:")
                    for k, v in value.items():
                        print(f"    {k}: {v}")
                elif isinstance(value, float):
                    if 'percentage' in key or 'rate' in key:
                        print(f"  {key.replace('_', ' ').title()}: {value:.2f}%")
                    else:
                        print(f"  {key.replace('_', ' ').title()}: {value:.4f}")
                else:
                    print(f"  {key.replace('_', ' ').title()}: {value}")
            
            return True
        else:
            print(f"Analysis failed: {response.text}")
            
    except Exception as e:
        print(f"Test failed: {e}")
    
    return False

def test_with_file_upload():
    """Test the server with file upload"""
    try:
        htm_file = Path("10.htm")
        if not htm_file.exists():
            print(f"File not found: {htm_file}")
            return False
            
        with open(htm_file, 'rb') as f:
            files = {'file': ('10.htm', f, 'text/html')}
            
            response = requests.post(
                "http://localhost:8000/api/v1/mt4/analyze/file",
                files=files,
                params={
                    "calculate_r_multiple": True,
                    "include_open_trades": True
                },
                timeout=30
            )
        
        print(f"File upload analysis response: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print("✅ File upload analysis successful!")
            return True
        else:
            print(f"File upload analysis failed: {response.text}")
            
    except Exception as e:
        print(f"File upload test failed: {e}")
    
    return False

def main():
    """Main test function"""
    print("🚀 Testing FastAPI server with 10.htm file...")
    
    # Wait a bit for server to start
    print("Waiting for server to start...")
    time.sleep(3)
    
    # Test server health
    if not test_server_health():
        print("❌ Server is not running. Please start it first.")
        return
    
    # Test with file path
    print("\n📁 Testing with file path...")
    path_success = test_with_htm_file()
    
    # Test with file upload
    print("\n📤 Testing with file upload...")
    upload_success = test_with_file_upload()
    
    # Summary
    print("\n📊 Test Summary:")
    print(f"  - Path analysis: {'✅ PASS' if path_success else '❌ FAIL'}")
    print(f"  - Upload analysis: {'✅ PASS' if upload_success else '❌ FAIL'}")
    
    if path_success or upload_success:
        print("\n🎉 Server is working correctly with 10.htm file!")
    else:
        print("\n❌ Tests failed. Check server logs for details.")

if __name__ == "__main__":
    main()
