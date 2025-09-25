#!/usr/bin/env python3
"""
Test script for Travel Assistant MCP Server
Tests both REST API endpoints and MCP protocol endpoints
"""

import requests
import json
import asyncio
import aiohttp
import sys
from datetime import datetime, timedelta

# Server configuration
SERVER_URL = "https://travel-mind-mcp.onrender.com"
# For local testing, change to: SERVER_URL = "http://localhost:8000"

def print_test_header(test_name):
    print(f"\n{'='*60}")
    print(f"🧪 TESTING: {test_name}")
    print(f"{'='*60}")

def print_result(success, message, data=None):
    status = "✅ PASS" if success else "❌ FAIL"
    print(f"{status}: {message}")
    if data and isinstance(data, dict):
        print(f"Response: {json.dumps(data, indent=2)[:200]}...")
    elif data:
        print(f"Response: {str(data)[:200]}...")
    print()

def test_server_health():
    """Test basic server health and info"""
    print_test_header("Server Health Check")
    
    try:
        # Test root endpoint
        response = requests.get(f"{SERVER_URL}/", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print_result(True, "Server is running", data)
            return True
        else:
            print_result(False, f"Server returned {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print_result(False, f"Connection error: {str(e)}")
        return False

def test_health_endpoint():
    """Test health endpoint"""
    print_test_header("Health Endpoint")
    
    try:
        response = requests.get(f"{SERVER_URL}/health", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print_result(True, "Health check passed", data)
            return True
        else:
            print_result(False, f"Health check failed with {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print_result(False, f"Health check error: {str(e)}")
        return False

def test_flight_search():
    """Test flight search API"""
    print_test_header("Flight Search API")
    
    try:
        # Sample flight search data
        flight_data = {
            "departure_id": "JFK",
            "arrival_id": "LAX",
            "outbound_date": "2024-12-15",
            "adults": 1
        }
        
        response = requests.post(
            f"{SERVER_URL}/search-flights",
            json=flight_data,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                print_result(True, "Flight search successful", data)
                return True
            else:
                print_result(False, f"Flight search failed: {data.get('error')}", data)
                return False
        else:
            print_result(False, f"Flight search returned {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print_result(False, f"Flight search error: {str(e)}")
        return False

def test_hotel_search():
    """Test hotel search API"""
    print_test_header("Hotel Search API")
    
    try:
        # Sample hotel search data
        hotel_data = {
            "location": "New York",
            "check_in_date": "2024-12-20",
            "check_out_date": "2024-12-23",
            "adults": 2
        }
        
        response = requests.post(
            f"{SERVER_URL}/search-hotels",
            json=hotel_data,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                print_result(True, "Hotel search successful", data)
                return True
            else:
                print_result(False, f"Hotel search failed: {data.get('error')}", data)
                return False
        else:
            print_result(False, f"Hotel search returned {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print_result(False, f"Hotel search error: {str(e)}")
        return False

def test_weather_api():
    """Test weather API"""
    print_test_header("Weather API")
    
    try:
        response = requests.get(
            f"{SERVER_URL}/weather/current",
            params={"location": "New York"},
            timeout=15
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                print_result(True, "Weather API successful", data)
                return True
            else:
                print_result(False, f"Weather API failed: {data.get('error')}", data)
                return False
        else:
            print_result(False, f"Weather API returned {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print_result(False, f"Weather API error: {str(e)}")
        return False

def test_currency_conversion():
    """Test currency conversion API"""
    print_test_header("Currency Conversion API")
    
    try:
        response = requests.get(
            f"{SERVER_URL}/finance/convert-currency",
            params={
                "from_currency": "USD",
                "to_currency": "EUR",
                "amount": 100
            },
            timeout=15
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                print_result(True, "Currency conversion successful", data)
                return True
            else:
                print_result(False, f"Currency conversion failed: {data.get('error')}", data)
                return False
        else:
            print_result(False, f"Currency API returned {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print_result(False, f"Currency API error: {str(e)}")
        return False

def test_geocoding_api():
    """Test geocoding API"""
    print_test_header("Geocoding API")
    
    try:
        response = requests.get(
            f"{SERVER_URL}/geocoding/geocode",
            params={"location": "Times Square, New York"},
            timeout=15
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                print_result(True, "Geocoding successful", data)
                return True
            else:
                print_result(False, f"Geocoding failed: {data.get('error')}", data)
                return False
        else:
            print_result(False, f"Geocoding API returned {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print_result(False, f"Geocoding API error: {str(e)}")
        return False

async def test_mcp_sse_endpoint():
    """Test MCP SSE endpoint"""
    print_test_header("MCP SSE Endpoint")
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(f"{SERVER_URL}/sse") as response:
                if response.status == 200:
                    print_result(True, "MCP SSE endpoint is accessible")
                    
                    # Read a few events
                    event_count = 0
                    async for line in response.content:
                        if event_count >= 3:  # Read first 3 events
                            break
                        
                        line_str = line.decode('utf-8').strip()
                        if line_str.startswith('data:'):
                            try:
                                event_data = json.loads(line_str[5:])  # Remove 'data:' prefix
                                print(f"📡 Received event: {event_data.get('type', 'unknown')}")
                                event_count += 1
                            except json.JSONDecodeError:
                                continue
                    
                    print_result(True, f"Successfully received {event_count} MCP events")
                    return True
                else:
                    print_result(False, f"MCP SSE endpoint returned {response.status}")
                    return False
    except Exception as e:
        print_result(False, f"MCP SSE endpoint error: {str(e)}")
        return False

def test_mcp_tool_execution():
    """Test MCP tool execution endpoint"""
    print_test_header("MCP Tool Execution")
    
    try:
        # Test geocoding tool (least likely to require API keys)
        tool_data = {
            "name": "geocode_location",
            "input": {
                "location": "Empire State Building, New York"
            }
        }
        
        response = requests.post(
            f"{SERVER_URL}/mcp/tool",
            json=tool_data,
            timeout=15
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                print_result(True, "MCP tool execution successful", data)
                return True
            else:
                print_result(False, f"MCP tool execution failed: {data.get('error')}", data)
                return False
        else:
            print_result(False, f"MCP tool endpoint returned {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print_result(False, f"MCP tool execution error: {str(e)}")
        return False

def generate_claude_api_example():
    """Generate example Claude API code"""
    print_test_header("Claude API Integration Example")
    
    example_code = f'''
# Example: Using your MCP server with Claude API

import anthropic

client = anthropic.Anthropic()

response = client.beta.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=1000,
    messages=[
        {{
            "role": "user",
            "content": "Search for flights from JFK to LAX on December 15th"
        }}
    ],
    mcp_servers=[
        {{
            "type": "url",
            "url": "{SERVER_URL}/sse",
            "name": "travel-assistant",
            "tool_configuration": {{
                "enabled": True,
                "allowed_tools": [
                    "search_flights",
                    "search_hotels",
                    "get_current_weather",
                    "search_events",
                    "convert_currency",
                    "geocode_location"
                ]
            }}
        }}
    ],
    betas=["mcp-client-2025-04-04"]
)

print(response.content)
'''
    
    print("🔗 Claude API Integration Code:")
    print(example_code)

async def main():
    """Run all tests"""
    print("🚀 Starting Travel Assistant MCP Server Tests")
    print(f"🌐 Testing server: {SERVER_URL}")
    
    # Basic connectivity tests
    tests_passed = 0
    total_tests = 0
    
    # Test basic endpoints
    basic_tests = [
        test_server_health,
        test_health_endpoint,
    ]
    
    for test_func in basic_tests:
        total_tests += 1
        if test_func():
            tests_passed += 1
    
    # Test REST API endpoints (these might fail without API keys)
    api_tests = [
        test_flight_search,
        test_hotel_search,
        test_weather_api,
        test_currency_conversion,
        test_geocoding_api,
    ]
    
    print_test_header("REST API Tests (may fail without API keys)")
    for test_func in api_tests:
        total_tests += 1
        if test_func():
            tests_passed += 1
    
    # Test MCP protocol endpoints
    total_tests += 1
    if await test_mcp_sse_endpoint():
        tests_passed += 1
    
    total_tests += 1
    if test_mcp_tool_execution():
        tests_passed += 1
    
    # Generate Claude API example
    generate_claude_api_example()
    
    # Summary
    print_test_header("Test Summary")
    print(f"✅ Tests Passed: {tests_passed}/{total_tests}")
    print(f"📊 Success Rate: {(tests_passed/total_tests)*100:.1f}%")
    
    if tests_passed == total_tests:
        print("🎉 All tests passed! Your MCP server is working perfectly!")
    elif tests_passed >= total_tests * 0.5:
        print("⚠️  Most tests passed. Some API endpoints may need API keys configured.")
    else:
        print("🚨 Several tests failed. Check server configuration and API keys.")
    
    return tests_passed, total_tests

if __name__ == "__main__":
    # Install required packages if not available
    try:
        import aiohttp
    except ImportError:
        print("Installing required packages...")
        import subprocess
        subprocess.run([sys.executable, "-m", "pip", "install", "aiohttp"])
        import aiohttp
    
    # Run the tests
    asyncio.run(main())