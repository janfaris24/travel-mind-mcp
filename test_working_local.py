#!/usr/bin/env python3
"""
Test the working MCP implementation locally
"""

import os
import time
import subprocess
import requests
from dotenv import load_dotenv
import anthropic
import sys

# Load environment variables
load_dotenv()

def test_working_implementation():
    """Test the working MCP implementation"""
    print("🧪 Testing WORKING MCP Implementation")
    
    # Start local server
    print("🚀 Starting working MCP server...")
    process = subprocess.Popen([
        sys.executable, "main_working.py"
    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    # Wait for server to start
    time.sleep(3)
    
    try:
        # Test basic connectivity
        print("🔍 Testing basic connectivity...")
        response = requests.get("http://localhost:8000/", timeout=5)
        if response.status_code == 200:
            print("✅ Server responding")
        else:
            print(f"❌ Server returned {response.status_code}")
            return False
        
        # Test Claude API
        print("🧪 Testing Claude API integration...")
        client = anthropic.Anthropic()
        
        response = client.beta.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=300,
            messages=[
                {
                    "role": "user",
                    "content": "Hello! What travel tools do you have available?"
                }
            ],
            mcp_servers=[
                {
                    "type": "url",
                    "url": "http://localhost:8000/sse",
                    "name": "travel-assistant"
                }
            ],
            betas=["mcp-client-2025-04-04"]
        )
        
        print("✅ SUCCESS! Working implementation connects to Claude!")
        print(f"📝 Response: {response.content[0].text[:200]}...")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        return False
        
    finally:
        # Cleanup
        print("🛑 Stopping server...")
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()

if __name__ == "__main__":
    success = test_working_implementation()
    
    if success:
        print("\n🎉 WORKING IMPLEMENTATION SUCCESSFUL!")
        print("✅ Ready to deploy to Render")
    else:
        print("\n🚨 Still needs fixes")