#!/usr/bin/env python3
"""
Debug test for MCP server - check basic connectivity first
"""

import requests
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_server_basic():
    """Test basic server connectivity"""
    print("🔍 Step 1: Testing basic server connectivity...")
    
    try:
        response = requests.get("https://travel-mind-mcp.onrender.com/", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print("✅ Server is running!")
            print(f"   Services: {data.get('services', [])}")
            return True
        else:
            print(f"❌ Server returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Basic connectivity failed: {str(e)}")
        return False

def test_health_endpoint():
    """Test health endpoint"""
    print("\n🔍 Step 2: Testing health endpoint...")
    
    try:
        response = requests.get("https://travel-mind-mcp.onrender.com/health", timeout=10)
        if response.status_code == 200:
            print("✅ Health endpoint working!")
            return True
        else:
            print(f"❌ Health endpoint returned {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check failed: {str(e)}")
        return False

def test_sse_endpoint():
    """Test SSE endpoint basic connectivity"""
    print("\n🔍 Step 3: Testing SSE endpoint...")
    
    try:
        # Try a simple POST to the SSE endpoint with timeout
        response = requests.post(
            "https://travel-mind-mcp.onrender.com/sse", 
            timeout=5,
            stream=True
        )
        print(f"   SSE endpoint status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ SSE endpoint is accessible!")
            
            # Try to read first few bytes
            print("   Reading first response...")
            start_time = time.time()
            
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    print(f"   Received data: {chunk[:100]}...")
                    break
                
                # Timeout after 3 seconds
                if time.time() - start_time > 3:
                    print("   ⏰ Timeout reading response")
                    break
            
            return True
        else:
            print(f"❌ SSE endpoint returned {response.status_code}")
            return False
    except requests.exceptions.Timeout:
        print("⏰ SSE endpoint timed out (this might be normal for streaming)")
        return True  # Timeout on streaming might be OK
    except Exception as e:
        print(f"❌ SSE endpoint failed: {str(e)}")
        return False

def test_claude_api_simple():
    """Test Claude API without MCP server"""
    print("\n🔍 Step 4: Testing Claude API (without MCP)...")
    
    try:
        import anthropic
        client = anthropic.Anthropic()
        
        response = client.beta.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=50,
            messages=[{"role": "user", "content": "Hello! Just say hi back."}],
            betas=["mcp-client-2025-04-04"]
        )
        
        print("✅ Claude API working!")
        print(f"   Response: {response.content[0].text[:50]}...")
        return True
        
    except Exception as e:
        print(f"❌ Claude API failed: {str(e)}")
        return False

def main():
    """Run diagnostic tests"""
    print("🔧 MCP Server Diagnostic Tests")
    print("=" * 50)
    
    results = []
    
    # Test basic connectivity
    results.append(("Basic Server", test_server_basic()))
    
    # Test health endpoint
    results.append(("Health Endpoint", test_health_endpoint()))
    
    # Test SSE endpoint
    results.append(("SSE Endpoint", test_sse_endpoint()))
    
    # Test Claude API
    results.append(("Claude API", test_claude_api_simple()))
    
    # Summary
    print("\n" + "=" * 50)
    print("🏁 DIAGNOSTIC SUMMARY")
    print("=" * 50)
    
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} {test_name}")
    
    passed_count = sum(1 for _, passed in results if passed)
    total_count = len(results)
    
    print(f"\n📊 {passed_count}/{total_count} tests passed")
    
    if passed_count == total_count:
        print("🎉 All diagnostics passed! The issue might be with MCP protocol specifics.")
        print("💡 Try testing with a simpler MCP request or check server logs.")
    elif passed_count >= 2:
        print("⚠️  Basic connectivity works, but there may be MCP-specific issues.")
    else:
        print("🚨 Multiple connectivity issues detected.")

if __name__ == "__main__":
    main()