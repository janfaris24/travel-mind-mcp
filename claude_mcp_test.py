#!/usr/bin/env python3
"""
Test Claude API with Travel Assistant MCP Server
This script tests the integration between Claude API and your hosted MCP server
"""

import os
import sys
import json
from datetime import datetime, timedelta

# Check if required packages are installed
try:
    import anthropic
except ImportError:
    print("Installing anthropic package...")
    import subprocess
    subprocess.run([sys.executable, "-m", "pip", "install", "anthropic"])
    import anthropic

try:
    from dotenv import load_dotenv
except ImportError:
    print("Installing python-dotenv package...")
    import subprocess
    subprocess.run([sys.executable, "-m", "pip", "install", "python-dotenv"])
    from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configuration
MCP_SERVER_URL = "https://travel-mind-mcp.onrender.com/sse"

def get_api_key():
    """Get Claude API key from environment or user input"""
    api_key = os.getenv('ANTHROPIC_API_KEY')
    if not api_key:
        print("🔑 Claude API key not found in environment.")
        print("Please set ANTHROPIC_API_KEY environment variable or enter it below:")
        api_key = input("Enter your Claude API key: ").strip()
        if not api_key:
            print("❌ API key is required!")
            sys.exit(1)
    return api_key

def create_client():
    """Create Anthropic client"""
    api_key = get_api_key()
    return anthropic.Anthropic(api_key=api_key)

def print_test_header(test_name):
    """Print formatted test header"""
    print(f"\n{'='*60}")
    print(f"🧪 {test_name}")
    print(f"{'='*60}")

def print_response(response):
    """Pretty print Claude response"""
    print("📝 Claude Response:")
    print("-" * 40)
    
    for content in response.content:
        if hasattr(content, 'text'):
            print(content.text)
        elif hasattr(content, 'type'):
            if content.type == 'mcp_tool_use':
                print(f"🔧 Used tool: {content.name} from {content.server_name}")
                print(f"   Input: {json.dumps(content.input, indent=2)}")
            elif content.type == 'mcp_tool_result':
                print(f"✅ Tool result from {content.server_name}:")
                print(f"   {content.content[:200]}...")
        else:
            print(f"Content: {content}")
    
    print("-" * 40)
    print(f"📊 Usage - Input: {response.usage.input_tokens}, Output: {response.usage.output_tokens}")
    print()

def test_basic_connection():
    """Test basic connection to MCP server via Claude"""
    print_test_header("Basic MCP Connection Test")
    
    try:
        client = create_client()
        
        response = client.beta.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=500,
            messages=[
                {
                    "role": "user",
                    "content": "What tools do you have available from the travel assistant?"
                }
            ],
            mcp_servers=[
                {
                    "type": "url",
                    "url": MCP_SERVER_URL,
                    "name": "travel-assistant",
                    "tool_configuration": {
                        "enabled": True
                    }
                }
            ],
            betas=["mcp-client-2025-04-04"]
        )
        
        print("✅ Successfully connected to MCP server!")
        print_response(response)
        return True
        
    except Exception as e:
        print(f"❌ Failed to connect: {str(e)}")
        return False

def test_flight_search():
    """Test flight search via Claude + MCP"""
    print_test_header("Flight Search Test")
    
    try:
        client = create_client()
        
        # Get tomorrow's date for the search
        tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        
        response = client.beta.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1000,
            messages=[
                {
                    "role": "user",
                    "content": f"Search for flights from JFK to LAX on {tomorrow}. Show me a few options with prices."
                }
            ],
            mcp_servers=[
                {
                    "type": "url",
                    "url": MCP_SERVER_URL,
                    "name": "travel-assistant",
                    "tool_configuration": {
                        "enabled": True,
                        "allowed_tools": ["search_flights"]
                    }
                }
            ],
            betas=["mcp-client-2025-04-04"]
        )
        
        print("✅ Flight search completed!")
        print_response(response)
        return True
        
    except Exception as e:
        print(f"❌ Flight search failed: {str(e)}")
        return False

def test_hotel_search():
    """Test hotel search via Claude + MCP"""
    print_test_header("Hotel Search Test")
    
    try:
        client = create_client()
        
        # Get dates for hotel search
        checkin = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
        checkout = (datetime.now() + timedelta(days=10)).strftime("%Y-%m-%d")
        
        response = client.beta.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1000,
            messages=[
                {
                    "role": "user",
                    "content": f"Find hotels in Miami from {checkin} to {checkout} for 2 adults. Show me some good options."
                }
            ],
            mcp_servers=[
                {
                    "type": "url",
                    "url": MCP_SERVER_URL,
                    "name": "travel-assistant",
                    "tool_configuration": {
                        "enabled": True,
                        "allowed_tools": ["search_hotels"]
                    }
                }
            ],
            betas=["mcp-client-2025-04-04"]
        )
        
        print("✅ Hotel search completed!")
        print_response(response)
        return True
        
    except Exception as e:
        print(f"❌ Hotel search failed: {str(e)}")
        return False

def test_weather_and_currency():
    """Test weather and currency tools"""
    print_test_header("Weather & Currency Test")
    
    try:
        client = create_client()
        
        response = client.beta.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1000,
            messages=[
                {
                    "role": "user",
                    "content": "What's the current weather in Tokyo? Also convert 1000 USD to JPY for my trip budget."
                }
            ],
            mcp_servers=[
                {
                    "type": "url",
                    "url": MCP_SERVER_URL,
                    "name": "travel-assistant",
                    "tool_configuration": {
                        "enabled": True,
                        "allowed_tools": ["get_current_weather", "convert_currency"]
                    }
                }
            ],
            betas=["mcp-client-2025-04-04"]
        )
        
        print("✅ Weather and currency check completed!")
        print_response(response)
        return True
        
    except Exception as e:
        print(f"❌ Weather/currency test failed: {str(e)}")
        return False

def test_comprehensive_travel_planning():
    """Test comprehensive travel planning with multiple tools"""
    print_test_header("Comprehensive Travel Planning Test")
    
    try:
        client = create_client()
        
        response = client.beta.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1500,
            messages=[
                {
                    "role": "user",
                    "content": """I'm planning a trip to Tokyo. Can you help me:
                    1. Find the coordinates of Tokyo for my GPS
                    2. Check the current weather there
                    3. Convert 2000 USD to Japanese Yen for my budget
                    4. Search for any tech conferences or networking events happening there
                    
                    Please use your travel tools to help me plan this trip!"""
                }
            ],
            mcp_servers=[
                {
                    "type": "url",
                    "url": MCP_SERVER_URL,
                    "name": "travel-assistant",
                    "tool_configuration": {
                        "enabled": True,
                        "allowed_tools": [
                            "geocode_location",
                            "get_current_weather", 
                            "convert_currency",
                            "search_events"
                        ]
                    }
                }
            ],
            betas=["mcp-client-2025-04-04"]
        )
        
        print("✅ Comprehensive travel planning completed!")
        print_response(response)
        return True
        
    except Exception as e:
        print(f"❌ Comprehensive planning failed: {str(e)}")
        return False

def main():
    """Run all tests"""
    print("🚀 Testing Claude API with Travel Assistant MCP Server")
    print(f"🌐 MCP Server: {MCP_SERVER_URL}")
    print()
    
    # Check API key first
    try:
        api_key = get_api_key()
        if api_key.startswith('sk-'):
            print("✅ Claude API key detected")
        else:
            print("⚠️  API key format may be incorrect")
    except:
        print("❌ Cannot proceed without API key")
        return
    
    # Run tests
    tests_passed = 0
    total_tests = 5
    
    tests = [
        test_basic_connection,
        test_flight_search,
        test_hotel_search, 
        test_weather_and_currency,
        test_comprehensive_travel_planning
    ]
    
    for test_func in tests:
        try:
            if test_func():
                tests_passed += 1
        except KeyboardInterrupt:
            print("\n🛑 Tests interrupted by user")
            break
        except Exception as e:
            print(f"❌ Unexpected error: {str(e)}")
    
    # Summary
    print_test_header("Test Summary")
    print(f"✅ Tests Passed: {tests_passed}/{total_tests}")
    print(f"📊 Success Rate: {(tests_passed/total_tests)*100:.1f}%")
    
    if tests_passed == total_tests:
        print("🎉 Perfect! Your MCP server works flawlessly with Claude API!")
        print("🔗 Your server is ready for production use!")
    elif tests_passed >= 3:
        print("✅ Great! Most functionality works. Some API endpoints may need keys configured.")
    elif tests_passed >= 1:
        print("⚠️  Basic connection works, but some services may need API keys in Render.")
    else:
        print("🚨 Connection issues detected. Check your MCP server status.")
    
    print(f"\n📖 Your MCP server URL for Claude API: {MCP_SERVER_URL}")

if __name__ == "__main__":
    main()