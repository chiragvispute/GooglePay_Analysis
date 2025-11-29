#!/usr/bin/env python3
"""Quick test script to verify the API is working"""

import requests
import time

def test_api():
    base_url = "http://localhost:8000"
    
    # Wait a moment for server to start
    time.sleep(2)
    
    # Test health endpoint
    try:
        response = requests.get(f"{base_url}/health")
        print(f"Health check: {response.status_code} - {response.json()}")
    except Exception as e:
        print(f"Health check failed: {e}")
        return
    
    # Test analyze endpoint with sample data
    try:
        sample_html = """
        <div class="outer-cell mdl-shadow">
            <div class="mdl-typography--body-1">
                You paid ₹150.00 to Swiggy using HDFC Bank on 15 Nov 2024
            </div>
        </div>
        <div class="outer-cell mdl-shadow">
            <div class="mdl-typography--body-1">
                You paid ₹85.50 to Zomato using UPI on 14 Nov 2024
            </div>
        </div>
        """
        
        data = {
            "html_content": sample_html,
            "timeframe": "1month"
        }
        
        response = requests.post(f"{base_url}/analyze", json=data)
        print(f"\nAnalyze endpoint: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print("✅ Analysis successful!")
            print(f"Found {len(result.get('transactions', []))} transactions")
            if result.get('insights'):
                print("✅ CrewAI insights generated!")
        else:
            print(f"❌ Analysis failed: {response.text}")
            
    except Exception as e:
        print(f"Analyze test failed: {e}")

if __name__ == "__main__":
    test_api()