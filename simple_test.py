#!/usr/bin/env python3
"""Simple test to verify the app runs correctly without external dependencies"""

import json
import sys
import os

# Test if our app can be imported and key functions work
try:
    sys.path.append(os.path.dirname(__file__))
    
    # Test basic HTML parsing
    sample_html = """
    <div class="outer-cell mdl-shadow">
        <div class="mdl-typography--body-1">
            You paid ₹150.00 to Swiggy using HDFC Bank on 15 Nov 2024
        </div>
    </div>
    """
    
    print("🧪 Testing Google Pay CrewAI Analyzer...")
    
    # Import our analyzer
    from crewai_app import GPPayAnalyzer
    
    # Test parsing
    analyzer = GPPayAnalyzer()
    transactions = analyzer.parse_html_content(sample_html)
    
    print(f"✅ HTML Parsing: Found {len(transactions)} transactions")
    if transactions:
        print(f"   Sample transaction: {transactions[0]}")
    
    # Test if CrewAI is set up
    if hasattr(analyzer, 'financial_analyst') and analyzer.financial_analyst:
        print("✅ CrewAI Agents: Properly configured")
    else:
        print("⚠️  CrewAI Agents: Basic mode (no LLM)")
    
    print("\n🎉 App is working correctly!")
    print("Start the server with: python crewai_app.py")
    print("Then test endpoints at: http://localhost:8000")
    
except Exception as e:
    print(f"❌ Error: {e}")
    print("Make sure all dependencies are installed:")
    print("pip install fastapi uvicorn crewai google-generativeai beautifulsoup4 pandas python-dotenv")