#!/usr/bin/env python3
"""Test Gemini integration in the deployed app"""

import requests
import json

def test_gemini_analysis():
    """Test if Gemini AI is working in the deployed app"""
    
    base_url = "https://googlepay-analysis.onrender.com"
    
    # Sample Google Pay HTML content
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
    <div class="outer-cell mdl-shadow">
        <div class="mdl-typography--body-1">
            You paid ₹200.00 to Amazon using Credit Card on 13 Nov 2024
        </div>
    </div>
    """
    
    print("🧪 Testing Gemini AI Integration...")
    
    # Test 1: Health check
    try:
        response = requests.get(f"{base_url}/health")
        health = response.json()
        print(f"✅ Health Check: {health}")
        
        if health.get("ai_enabled") and health.get("ai_engine") == "CrewAI":
            print("✅ CrewAI is enabled in deployment")
        else:
            print("⚠️ AI might not be fully enabled")
            
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return
    
    # Test 2: Quick insights (simpler endpoint)
    try:
        # Create a file-like object for testing
        files = {
            'file': ('test.html', sample_html, 'text/html')
        }
        data = {
            'query': 'What are my spending patterns?',
            'timeframe': '1month'
        }
        
        response = requests.post(f"{base_url}/quick-insights", files=files, data=data)
        print(f"\n📊 Quick Insights Response (Status: {response.status_code}):")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Analysis successful!")
            print(f"📈 Transactions found: {len(result.get('transactions', []))}")
            
            if result.get('insights'):
                print("🤖 Gemini AI insights generated:")
                print(result['insights'][:200] + "..." if len(result['insights']) > 200 else result['insights'])
            else:
                print("⚠️ No AI insights - might be using basic mode")
                
        else:
            print(f"❌ Request failed: {response.text}")
            
    except Exception as e:
        print(f"❌ Analysis test failed: {e}")
        
    # Test 3: Full analyze endpoint with file upload
    try:
        files = {
            'file': ('gpay.html', sample_html, 'text/html')
        }
        data = {
            'query': 'Analyze my Google Pay transactions and provide financial insights',
            'timeframe': '1month'
        }
        
        response = requests.post(f"{base_url}/analyze", files=files, data=data)
        print(f"\n🔍 Full Analysis Response (Status: {response.status_code}):")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Full analysis successful!")
            
            if result.get('crewai_insights'):
                print("🤖 CrewAI Multi-Agent Analysis:")
                insights = result['crewai_insights']
                print(f"📊 AI Insights: {insights[:300]}..." if len(insights) > 300 else insights)
                print("✅ Gemini is working with CrewAI agents!")
            elif result.get('basic_analysis'):
                print("⚠️ Basic analysis mode - AI agents might not be initialized")
            else:
                print(f"Response preview: {str(result)[:200]}...")
                
        else:
            print(f"❌ Full analysis failed: {response.text}")
            
    except Exception as e:
        print(f"❌ Full analysis test failed: {e}")

if __name__ == "__main__":
    test_gemini_analysis()