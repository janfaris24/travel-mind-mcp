#!/usr/bin/env python3
"""
Test actual tool usage with the fixed MCP server
"""

import os
from dotenv import load_dotenv
import anthropic

# Load environment variables
load_dotenv()

def test_geocoding_tool():
    """Test the geocoding tool (most likely to work without API keys)"""
    try:
        client = anthropic.Anthropic()
        
        print("🧪 Testing Geocoding Tool...")
        
        response = client.beta.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=500,
            messages=[
                {
                    "role": "user",
                    "content": "Can you find the coordinates for 'Times Square, New York'? Use your geocoding tool."
                }
            ],
            mcp_servers=[
                {
                    "type": "url",
                    "url": "https://travel-mind-mcp.onrender.com/sse",
                    "name": "travel-assistant",
                    "tool_configuration": {
                        "enabled": True,
                        "allowed_tools": ["geocode_location"]
                    }
                }
            ],
            betas=["mcp-client-2025-04-04"]
        )
        
        print("✅ Tool execution successful!")
        print("\n📝 Response:")
        for content in response.content:
            if hasattr(content, 'text'):
                print(content.text)
        
        return True
        
    except Exception as e:
        print(f"❌ Tool test failed: {str(e)}")
        return False

def test_weather_tool():
    """Test the weather tool"""
    try:
        client = anthropic.Anthropic()
        
        print("\n🧪 Testing Weather Tool...")
        
        response = client.beta.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=500,
            messages=[
                {
                    "role": "user",
                    "content": "What's the current weather in Tokyo? Use your weather tool."
                }
            ],
            mcp_servers=[
                {
                    "type": "url",
                    "url": "https://travel-mind-mcp.onrender.com/sse",
                    "name": "travel-assistant",
                    "tool_configuration": {
                        "enabled": True,
                        "allowed_tools": ["get_current_weather"]
                    }
                }
            ],
            betas=["mcp-client-2025-04-04"]
        )
        
        print("✅ Weather tool executed!")
        print("\n📝 Response:")
        for content in response.content:
            if hasattr(content, 'text'):
                print(content.text)
        
        return True
        
    except Exception as e:
        print(f"❌ Weather tool failed: {str(e)}")
        return False

def main():
    """Run tool tests"""
    print("🛠️  Testing MCP Tools")
    print("=" * 50)
    
    tests_passed = 0
    
    # Test individual tools
    if test_geocoding_tool():
        tests_passed += 1
    
    if test_weather_tool():
        tests_passed += 1
    
    print(f"\n📊 Results: {tests_passed}/2 tool tests passed")
    
    if tests_passed == 2:
        print("🎉 All tools working! Your MCP server is fully functional!")
    elif tests_passed == 1:
        print("✅ Some tools working! Check API keys for failed tools.")
    else:
        print("🚨 Tool execution issues. Check server logs.")

if __name__ == "__main__":
    main()