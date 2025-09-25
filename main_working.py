#!/usr/bin/env python3
"""
Travel Assistant MCP Server - Working Implementation
Based on proven MCP patterns that work with Claude API
"""

import os
import sys
import json
import asyncio
from pathlib import Path
import uvicorn
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route

# Add all server directories to Python path
current_dir = Path(__file__).parent
sys.path.append(str(current_dir / "flight-search"))
sys.path.append(str(current_dir / "hotel-search"))
sys.path.append(str(current_dir / "weather-search"))
sys.path.append(str(current_dir / "event-search"))
sys.path.append(str(current_dir / "finance-search"))
sys.path.append(str(current_dir / "geocoder"))

class TravelMCPServer:
    def __init__(self):
        self.server_info = {
            "name": "travel-assistant",
            "version": "1.0.0"
        }
        
        # Define all travel tools
        self.tools = [
            {
                "name": "search_flights",
                "description": "Search for flights between airports",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "departure_id": {"type": "string", "description": "Departure airport code"},
                        "arrival_id": {"type": "string", "description": "Arrival airport code"},
                        "outbound_date": {"type": "string", "description": "Departure date YYYY-MM-DD"},
                        "return_date": {"type": "string", "description": "Return date YYYY-MM-DD (optional)"},
                        "adults": {"type": "integer", "default": 1}
                    },
                    "required": ["departure_id", "arrival_id", "outbound_date"]
                }
            },
            {
                "name": "search_hotels",
                "description": "Search for hotels in a location",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "location": {"type": "string", "description": "Location to search hotels"},
                        "check_in_date": {"type": "string", "description": "Check-in date YYYY-MM-DD"},
                        "check_out_date": {"type": "string", "description": "Check-out date YYYY-MM-DD"},
                        "adults": {"type": "integer", "default": 2}
                    },
                    "required": ["location", "check_in_date", "check_out_date"]
                }
            },
            {
                "name": "get_current_weather",
                "description": "Get current weather for a location",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "location": {"type": "string", "description": "Location name or coordinates"}
                    },
                    "required": ["location"]
                }
            },
            {
                "name": "search_events",
                "description": "Search for events",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Event search query"},
                        "location": {"type": "string", "description": "Location to search (optional)"}
                    },
                    "required": ["query"]
                }
            },
            {
                "name": "convert_currency",
                "description": "Convert currency amounts",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "from_currency": {"type": "string", "description": "Source currency code"},
                        "to_currency": {"type": "string", "description": "Target currency code"},
                        "amount": {"type": "number", "default": 1.0}
                    },
                    "required": ["from_currency", "to_currency"]
                }
            },
            {
                "name": "geocode_location",
                "description": "Get coordinates for a location",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "location": {"type": "string", "description": "Location to geocode"}
                    },
                    "required": ["location"]
                }
            }
        ]
    
    async def handle_request(self, request: Request):
        """Handle MCP JSON-RPC requests"""
        try:
            body = await request.json()
            method = body.get("method")
            id_ = body.get("id")
            
            print(f"📨 Received MCP request: {method}")
            
            if method == "initialize":
                return self.handle_initialize(body, id_)
            elif method == "tools/list":
                return self.handle_tools_list(id_)
            elif method == "tools/call":
                return await self.handle_tools_call(body, id_)
            else:
                return JSONResponse({
                    "jsonrpc": "2.0",
                    "id": id_,
                    "error": {"code": -32601, "message": f"Method '{method}' not found"}
                })
        
        except Exception as e:
            print(f"❌ Error handling request: {e}")
            return JSONResponse({
                "jsonrpc": "2.0",
                "id": body.get("id", 0) if 'body' in locals() else 0,
                "error": {"code": -32603, "message": f"Internal error: {str(e)}"}
            })
    
    def handle_initialize(self, body, id_):
        """Handle initialize request"""
        print("🔧 Handling initialize")
        return JSONResponse({
            "jsonrpc": "2.0",
            "id": id_,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "tools": {"listChanged": True},
                    "resources": {},
                    "prompts": {},
                    "logging": {}
                },
                "serverInfo": self.server_info
            }
        })
    
    def handle_tools_list(self, id_):
        """Handle tools/list request"""
        print("🛠️  Handling tools/list")
        return JSONResponse({
            "jsonrpc": "2.0",
            "id": id_,
            "result": {
                "tools": self.tools
            }
        })
    
    async def handle_tools_call(self, body, id_):
        """Handle tools/call request"""
        params = body.get("params", {})
        tool_name = params.get("name")
        tool_arguments = params.get("arguments", {})
        
        print(f"🔧 Executing tool: {tool_name}")
        
        try:
            result = await self.execute_tool(tool_name, tool_arguments)
            
            return JSONResponse({
                "jsonrpc": "2.0",
                "id": id_,
                "result": {
                    "content": [
                        {
                            "type": "text",
                            "text": json.dumps(result, indent=2) if isinstance(result, (dict, list)) else str(result)
                        }
                    ],
                    "isError": False
                }
            })
            
        except Exception as e:
            print(f"❌ Tool execution failed: {e}")
            return JSONResponse({
                "jsonrpc": "2.0",
                "id": id_,
                "result": {
                    "content": [
                        {
                            "type": "text",
                            "text": f"Error executing {tool_name}: {str(e)}"
                        }
                    ],
                    "isError": True
                }
            })
    
    async def execute_tool(self, tool_name, arguments):
        """Execute the specified tool"""
        if tool_name == "search_flights":
            from flight_server import search_flights
            return search_flights(**arguments)
            
        elif tool_name == "search_hotels":
            from hotel_server import search_hotels
            return search_hotels(**arguments)
            
        elif tool_name == "get_current_weather":
            from weatherstack_server import get_current_weather
            return get_current_weather(**arguments)
            
        elif tool_name == "search_events":
            from event_server import search_events
            return search_events(**arguments)
            
        elif tool_name == "convert_currency":
            from finance_server import convert_currency
            return convert_currency(**arguments)
            
        elif tool_name == "geocode_location":
            from geocoder_server import geocode_location
            return geocode_location(**arguments)
            
        else:
            raise ValueError(f"Unknown tool: {tool_name}")

# Create MCP server instance
mcp_server = TravelMCPServer()

async def health_check(request):
    """Health check endpoint"""
    return JSONResponse({"status": "healthy", "message": "MCP Server running"})

async def server_info(request):
    """Server info endpoint"""
    return JSONResponse({
        "message": "Travel Assistant MCP Server",
        "version": "1.0.0",
        "protocol": "MCP 2024-11-05",
        "transport": "HTTP/JSON-RPC",
        "tools_count": len(mcp_server.tools),
        "mcp_endpoint": "/sse"
    })

# Create Starlette app
app = Starlette(
    routes=[
        Route("/", server_info),
        Route("/health", health_check),
        Route("/sse", mcp_server.handle_request, methods=["POST"]),
    ]
)

def main():
    """Main entry point"""
    print("Travel Assistant MCP Server (Working Implementation)")
    print("Based on proven MCP patterns")
    
    # Get port from environment variable
    port_str = os.getenv("PORT", "8000")
    if port_str == "" or port_str is None:
        port = 8000
    else:
        try:
            port = int(port_str)
        except ValueError:
            print(f"Invalid PORT value: '{port_str}', using default 8000")
            port = 8000
    
    host = "0.0.0.0"
    
    print(f"Starting server on {host}:{port}")
    print("MCP Endpoint: POST /sse")
    print("Protocol: MCP 2024-11-05 with JSON-RPC 2.0")
    print(f"Tools available: {len(mcp_server.tools)}")
    
    # Start the server
    uvicorn.run(app, host=host, port=port)

if __name__ == "__main__":
    main()