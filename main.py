#!/usr/bin/env python3
"""
Travel Assistant MCP Server - Fixed Protocol Implementation
A comprehensive MCP server providing travel-related services following proper MCP spec
"""

import os
import sys
import json
import asyncio
import uuid
from pathlib import Path
import uvicorn
from fastapi import FastAPI, Request, Response
from sse_starlette.sse import EventSourceResponse

# Add all server directories to Python path
current_dir = Path(__file__).parent
sys.path.append(str(current_dir / "flight-search"))
sys.path.append(str(current_dir / "hotel-search"))
sys.path.append(str(current_dir / "weather-search"))
sys.path.append(str(current_dir / "event-search"))
sys.path.append(str(current_dir / "finance-search"))
sys.path.append(str(current_dir / "geocoder"))

def create_app():
    """Create the main FastAPI application with proper MCP protocol support"""
    
    # Create main app
    app = FastAPI(
        title="Travel Assistant MCP Server",
        version="1.0.0",
        description="Travel services MCP server providing flight search and other travel tools"
    )
    
    # Global session storage
    mcp_sessions = {}
    
    @app.get("/")
    async def root():
        return {
            "message": "Travel Assistant MCP Server",
            "version": "1.0.0",
            "status": "running",
            "services": ["flight-search", "hotel-search", "weather", "events", "finance", "geocoding"],
            "mcp_endpoint": "/sse",
            "protocol": "MCP 2024-11-05"
        }
    
    @app.get("/health")
    async def health():
        return {"status": "healthy", "message": "Server is running"}
    
    # Proper MCP SSE Endpoint
    @app.get("/sse")
    async def mcp_sse_endpoint(request: Request):
        """MCP Server-Sent Events endpoint following proper MCP protocol"""
        
        # Generate session ID
        session_id = str(uuid.uuid4())
        
        async def generate_mcp_events():
            try:
                # Send initial endpoint event with messages URL (required by MCP spec)
                yield {
                    "event": "endpoint",
                    "data": f"/sse/messages?session_id={session_id}"
                }
                
                # Keep connection alive with periodic pings
                while True:
                    await asyncio.sleep(30)  # Ping every 30 seconds
                    yield {
                        "event": "ping",
                        "data": "Server alive"
                    }
                    
            except asyncio.CancelledError:
                # Cleanup session on disconnect
                if session_id in mcp_sessions:
                    del mcp_sessions[session_id]
                raise
            except Exception as e:
                yield {
                    "event": "error", 
                    "data": f"Server error: {str(e)}"
                }
        
        return EventSourceResponse(
            generate_mcp_events(),
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "*",
            }
        )
    
    @app.post("/sse/messages")
    async def mcp_messages_endpoint(request: Request):
        """Handle MCP JSON-RPC messages according to protocol spec"""
        try:
            # Get session ID from query params
            session_id = request.query_params.get("session_id")
            if not session_id:
                return {"jsonrpc": "2.0", "error": {"code": -32602, "message": "Missing session_id"}}
            
            # Parse JSON-RPC request
            data = await request.json()
            request_id = data.get("id", 0)
            
            # Handle initialize request
            if data.get("method") == "initialize":
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {
                            "tools": {"listChanged": True},
                            "resources": {},
                            "prompts": {},
                            "logging": {}
                        },
                        "serverInfo": {
                            "name": "travel-assistant",
                            "version": "1.0.0"
                        }
                    }
                }
            
            # Handle tools/list request
            elif data.get("method") == "tools/list":
                tools = [
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
                
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "tools": tools
                    }
                }
            
            # Handle tools/call request
            elif data.get("method") == "tools/call":
                params = data.get("params", {})
                tool_name = params.get("name")
                tool_arguments = params.get("arguments", {})
                
                try:
                    # Route to appropriate tool function
                    result = None
                    
                    if tool_name == "search_flights":
                        from flight_server import search_flights
                        result = search_flights(**tool_arguments)
                        
                    elif tool_name == "search_hotels":
                        from hotel_server import search_hotels
                        result = search_hotels(**tool_arguments)
                        
                    elif tool_name == "get_current_weather":
                        from weatherstack_server import get_current_weather
                        result = get_current_weather(**tool_arguments)
                        
                    elif tool_name == "search_events":
                        from event_server import search_events
                        result = search_events(**tool_arguments)
                        
                    elif tool_name == "convert_currency":
                        from finance_server import convert_currency
                        result = convert_currency(**tool_arguments)
                        
                    elif tool_name == "geocode_location":
                        from geocoder_server import geocode_location
                        result = geocode_location(**tool_arguments)
                        
                    else:
                        raise ValueError(f"Unknown tool: {tool_name}")
                    
                    # Format result according to MCP spec
                    return {
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "result": {
                            "content": [
                                {
                                    "type": "text",
                                    "text": json.dumps(result, indent=2) if isinstance(result, (dict, list)) else str(result)
                                }
                            ],
                            "isError": False
                        }
                    }
                    
                except Exception as e:
                    return {
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "result": {
                            "content": [
                                {
                                    "type": "text", 
                                    "text": f"Error executing {tool_name}: {str(e)}"
                                }
                            ],
                            "isError": True
                        }
                    }
            
            else:
                # Unknown method
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {
                        "code": -32601,
                        "message": f"Method not found: {data.get('method')}"
                    }
                }
                
        except Exception as e:
            return {
                "jsonrpc": "2.0", 
                "id": data.get("id", 0) if 'data' in locals() else 0,
                "error": {
                    "code": -32603,
                    "message": f"Internal error: {str(e)}"
                }
            }
    
    return app

def main():
    """Main entry point"""
    print("Travel Assistant MCP Server (Fixed Protocol)")
    print("Initializing...")
    
    # Create the app
    app = create_app()
    
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
    print("MCP Endpoint: /sse")
    print("Protocol: MCP 2024-11-05 with proper JSON-RPC 2.0")
    
    # Start the server
    uvicorn.run(app, host=host, port=port)

if __name__ == "__main__":
    main()