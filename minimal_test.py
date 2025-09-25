#!/usr/bin/env python3
"""
Minimal test with timeout to avoid hanging
"""

import os
import asyncio
from dotenv import load_dotenv
import anthropic

# Load environment variables
load_dotenv()

async def test_with_timeout():
    """Test Claude API with MCP server with a timeout"""
    try:
        client = anthropic.Anthropic()
        
        print("🧪 Testing Claude API + MCP (with 30s timeout)...")
        
        # Create the request
        response = client.beta.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=200,
            messages=[
                {
                    "role": "user",
                    "content": "Hello! Can you list your available tools?"
                }
            ],
            mcp_servers=[
                {
                    "type": "url",
                    "url": "https://travel-mind-mcp.onrender.com/sse",
                    "name": "travel-assistant",
                    "tool_configuration": {
                        "enabled": True
                    }
                }
            ],
            betas=["mcp-client-2025-04-04"]
        )
        
        print("✅ SUCCESS! Got response from Claude + MCP")
        print("\n📝 Response:")
        for content in response.content:
            if hasattr(content, 'text'):
                print(content.text)
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def run_with_timeout():
    """Run the test with a timeout wrapper"""
    import signal
    
    def timeout_handler(signum, frame):
        print("\n⏰ Test timed out after 30 seconds")
        print("🔍 This suggests the MCP connection is hanging")
        raise TimeoutError("Test timed out")
    
    # Set up timeout
    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(30)  # 30 second timeout
    
    try:
        result = asyncio.run(test_with_timeout())
        signal.alarm(0)  # Cancel timeout
        return result
    except TimeoutError:
        return False
    except Exception as e:
        signal.alarm(0)  # Cancel timeout
        print(f"❌ Unexpected error: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 Starting minimal MCP test...")
    
    success = run_with_timeout()
    
    if success:
        print("\n🎉 MCP integration is working!")
    else:
        print("\n🚨 MCP integration has issues")
        print("\n💡 Possible solutions:")
        print("   1. The MCP server might need protocol adjustments")
        print("   2. Try using the REST API endpoints instead")
        print("   3. Check Render logs for MCP server errors")
        
        print("\n🔗 REST API endpoints work fine:")
        print("   - https://travel-mind-mcp.onrender.com/docs")
        print("   - https://travel-mind-mcp.onrender.com/search-flights")
        print("   - https://travel-mind-mcp.onrender.com/search-hotels")