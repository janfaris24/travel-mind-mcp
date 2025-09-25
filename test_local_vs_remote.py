#!/usr/bin/env python3
"""
Test local vs remote MCP server to isolate the issue
"""

import os
import time
import subprocess
import requests
from dotenv import load_dotenv
import anthropic
from threading import Thread
import signal
import sys

# Load environment variables
load_dotenv()

def start_local_server():
    """Start the MCP server locally"""
    print("🚀 Starting local MCP server...")
    
    # Start server in background
    process = subprocess.Popen([
        sys.executable, "main.py"
    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    # Wait a bit for server to start
    time.sleep(3)
    
    return process

def test_server_basic(server_url):
    """Test basic server connectivity"""
    print(f"🔍 Testing basic connectivity to {server_url}")
    
    try:
        response = requests.get(f"{server_url}/", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Server responding - Protocol: {data.get('protocol', 'unknown')}")
            return True
        else:
            print(f"❌ Server returned {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Connection failed: {str(e)}")
        return False

def test_sse_endpoint(server_url):
    """Test SSE endpoint"""
    print(f"🔍 Testing SSE endpoint at {server_url}/sse")
    
    try:
        response = requests.get(f"{server_url}/sse", timeout=5, stream=True)
        if response.status_code == 200:
            print(f"✅ SSE endpoint accessible (status: {response.status_code})")
            
            # Try to read first event
            for line in response.iter_lines(decode_unicode=True):
                if line.startswith('data:'):
                    print(f"📡 First event: {line[:50]}...")
                    break
                elif line.startswith('event:'):
                    print(f"📡 Event type: {line}")
                    
                # Don't hang forever
                break
            
            return True
        else:
            print(f"❌ SSE endpoint returned {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ SSE test failed: {str(e)}")
        return False

def test_claude_with_server(server_url, timeout=10):
    """Test Claude API with specific server URL"""
    print(f"🧪 Testing Claude API with {server_url}")
    
    try:
        client = anthropic.Anthropic()
        
        # Set a shorter timeout by using a simple request
        response = client.beta.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=100,
            messages=[
                {
                    "role": "user",
                    "content": "Hello! Just say hi and list any available tools briefly."
                }
            ],
            mcp_servers=[
                {
                    "type": "url",
                    "url": f"{server_url}/sse",
                    "name": "test-server"
                }
            ],
            betas=["mcp-client-2025-04-04"]
        )
        
        print("✅ Claude API connected successfully!")
        print(f"📝 Response: {response.content[0].text[:100]}...")
        return True
        
    except Exception as e:
        print(f"❌ Claude API failed: {str(e)}")
        return False

def run_with_timeout(func, timeout_seconds, *args, **kwargs):
    """Run function with timeout"""
    result = [None]
    exception = [None]
    
    def target():
        try:
            result[0] = func(*args, **kwargs)
        except Exception as e:
            exception[0] = e
    
    thread = Thread(target=target)
    thread.daemon = True
    thread.start()
    thread.join(timeout_seconds)
    
    if thread.is_alive():
        print(f"⏰ Function timed out after {timeout_seconds} seconds")
        return False
    
    if exception[0]:
        print(f"❌ Function failed: {exception[0]}")
        return False
        
    return result[0]

def main():
    """Run comprehensive local vs remote tests"""
    print("🔍 MCP Server Diagnosis: Local vs Remote")
    print("=" * 60)
    
    # Test remote server first
    print("\n1️⃣ TESTING REMOTE SERVER (Render)")
    print("-" * 40)
    
    remote_url = "https://travel-mind-mcp.onrender.com"
    remote_basic = test_server_basic(remote_url)
    remote_sse = test_sse_endpoint(remote_url)
    
    print(f"\nRemote server Claude test (15s timeout)...")
    remote_claude = run_with_timeout(test_claude_with_server, 15, remote_url)
    
    # Test local server
    print("\n2️⃣ TESTING LOCAL SERVER")
    print("-" * 40)
    
    local_process = None
    local_basic = False
    local_sse = False
    local_claude = False
    
    try:
        local_process = start_local_server()
        local_url = "http://localhost:8000"
        
        # Test local server
        local_basic = test_server_basic(local_url)
        if local_basic:
            local_sse = test_sse_endpoint(local_url)
            
            if local_sse:
                print(f"\nLocal server Claude test (15s timeout)...")
                local_claude = run_with_timeout(test_claude_with_server, 15, local_url)
        
    except Exception as e:
        print(f"❌ Local server startup failed: {e}")
    
    finally:
        # Cleanup local server
        if local_process:
            print("\n🛑 Stopping local server...")
            local_process.terminate()
            try:
                local_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                local_process.kill()
    
    # Results summary
    print("\n" + "=" * 60)
    print("📊 DIAGNOSIS RESULTS")
    print("=" * 60)
    
    print(f"Remote Server (Render):")
    print(f"  ✅ Basic connectivity: {'✅ PASS' if remote_basic else '❌ FAIL'}")
    print(f"  ✅ SSE endpoint: {'✅ PASS' if remote_sse else '❌ FAIL'}")
    print(f"  ✅ Claude integration: {'✅ PASS' if remote_claude else '❌ FAIL/TIMEOUT'}")
    
    print(f"\nLocal Server:")
    print(f"  ✅ Basic connectivity: {'✅ PASS' if local_basic else '❌ FAIL'}")
    print(f"  ✅ SSE endpoint: {'✅ PASS' if local_sse else '❌ FAIL'}")
    print(f"  ✅ Claude integration: {'✅ PASS' if local_claude else '❌ FAIL/TIMEOUT'}")
    
    # Diagnosis
    print(f"\n🔬 DIAGNOSIS:")
    
    if not remote_basic:
        print("🚨 Remote server is down or unreachable")
    elif not remote_sse:
        print("🚨 Remote SSE endpoint has issues")
    elif not remote_claude:
        if local_claude:
            print("🔍 ISSUE IS WITH RENDER DEPLOYMENT")
            print("   - Local works, remote doesn't")
            print("   - Check Render logs for errors")
            print("   - Possible network/firewall issues")
        else:
            print("🔍 ISSUE IS WITH MCP PROTOCOL IMPLEMENTATION")
            print("   - Both local and remote fail with Claude")
            print("   - Protocol needs further fixes")
    else:
        print("🎉 Everything works! No issues detected.")
    
    print(f"\n💡 NEXT STEPS:")
    if not remote_claude and not local_claude:
        print("   1. Fix MCP protocol implementation")
        print("   2. Check JSON-RPC message format")
        print("   3. Verify MCP spec compliance")
    elif not remote_claude and local_claude:
        print("   1. Check Render deployment logs")
        print("   2. Verify environment variables on Render")
        print("   3. Check Render networking/firewall")
    else:
        print("   1. Start using your working MCP server!")
        print("   2. Test individual tools")
        print("   3. Add more travel services")

if __name__ == "__main__":
    main()