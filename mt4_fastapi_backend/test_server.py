"""
Test script for the MT4 FastAPI backend server.
"""
import os
import requests
import time
import sys
import webbrowser
from urllib.parse import urljoin

def test_server(base_url="http://localhost:5501"):
    """Test if the server is running and responding to requests."""
    print(f"Testing server at {base_url}...")
    
    # Test health endpoint
    try:
        health_response = requests.get(urljoin(base_url, "/health"))
        print(f"Health check: {health_response.status_code}")
        print(f"Response: {health_response.json()}")
        
        if health_response.status_code == 200:
            print("\n✓ Server is running correctly!")
            return True
        else:
            print("\n✗ Server returned unexpected status code!")
            return False
    except requests.exceptions.ConnectionError:
        print("\n✗ Could not connect to server! Make sure it's running.")
        return False

def test_api_endpoints(base_url="http://localhost:5501"):
    """Test the API endpoints."""
    print("\nTesting API endpoints...")
    
    # Test API health endpoint
    try:
        api_health_response = requests.get(urljoin(base_url, "/api/v1/mt4/health"))
        print(f"API health check: {api_health_response.status_code}")
        print(f"Response: {api_health_response.json()}")
        
        if api_health_response.status_code == 200:
            print("\n✓ API endpoints are working correctly!")
            return True
        else:
            print("\n✗ API returned unexpected status code!")
            return False
    except requests.exceptions.ConnectionError:
        print("\n✗ Could not connect to API! Make sure it's running.")
        return False

def main():
    """Main function to run tests."""
    base_url = "http://localhost:5501"
    
    if len(sys.argv) > 1:
        base_url = sys.argv[1]
    
    server_running = test_server(base_url)
    
    if server_running:
        api_working = test_api_endpoints(base_url)
        
        if api_working:
            print("\nAll tests passed! Opening browser...")
            webbrowser.open(base_url)
        else:
            print("\nAPI tests failed. Please check the server logs.")
    else:
        print("\nServer tests failed. Please start the server first.")

if __name__ == "__main__":
    main()
