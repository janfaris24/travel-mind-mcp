#!/usr/bin/env python3
"""
Travel Assistant MCP Server
A comprehensive MCP server providing travel-related services including:
- Flight search and other travel services
"""

import os
import sys
import json
import asyncio
from pathlib import Path
import uvicorn
from fastapi import FastAPI, Request, Response
from fastapi.responses import StreamingResponse
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
    """Create the main FastAPI application"""
    
    # Create main app
    app = FastAPI(
        title="Travel Assistant MCP Server",
        version="1.0.0",
        description="Travel services MCP server providing flight search and other travel tools"
    )
    
    @app.get("/")
    async def root():
        return {
            "message": "Travel Assistant MCP Server",
            "version": "1.0.0",
            "status": "running",
            "services": ["flight-search", "hotel-search", "weather", "events", "finance", "geocoding"],
            "endpoints": {
                "/": "Service information",
                "/health": "Health check",
                "/docs": "API documentation"
            }
        }
    
    @app.get("/health")
    async def health():
        return {"status": "healthy", "message": "Server is running"}
    
    # Import and integrate the flight search tools
    try:
        from flight_server import search_flights, get_flight_details, filter_flights_by_price, filter_flights_by_airline
        
        # Add the flight search tools as API endpoints
        @app.post("/search-flights")
        async def api_search_flights(
            departure_id: str,
            arrival_id: str,
            outbound_date: str,
            return_date: str = None,
            trip_type: int = 1,
            adults: int = 1,
            children: int = 0,
            infants_in_seat: int = 0,
            infants_on_lap: int = 0,
            travel_class: int = 1,
            currency: str = "USD",
            country: str = "us",
            language: str = "en",
            max_results: int = 10
        ):
            """Search for flights"""
            try:
                result = search_flights(
                    departure_id=departure_id,
                    arrival_id=arrival_id,
                    outbound_date=outbound_date,
                    return_date=return_date,
                    trip_type=trip_type,
                    adults=adults,
                    children=children,
                    infants_in_seat=infants_in_seat,
                    infants_on_lap=infants_on_lap,
                    travel_class=travel_class,
                    currency=currency,
                    country=country,
                    language=language,
                    max_results=max_results
                )
                return {"success": True, "data": result}
            except Exception as e:
                return {"success": False, "error": str(e)}
        
        @app.get("/flight-details/{search_id}")
        async def api_get_flight_details(search_id: str):
            """Get detailed flight information"""
            try:
                result = get_flight_details(search_id)
                return {"success": True, "data": result}
            except Exception as e:
                return {"success": False, "error": str(e)}
        
        print("✓ Successfully integrated flight search tools")
        
    except Exception as e:
        print(f"Warning: Could not integrate flight search tools: {e}")
    
    # Hotel Search Integration
    try:
        from hotel_server import search_hotels, get_hotel_details
        
        @app.post("/search-hotels")
        async def api_search_hotels(
            location: str,
            check_in_date: str,
            check_out_date: str,
            adults: int = 2,
            children: int = 0,
            rooms: int = 1,
            currency: str = "USD",
            country: str = "us",
            language: str = "en",
            max_results: int = 10
        ):
            """Search for hotels"""
            try:
                result = search_hotels(
                    location=location,
                    check_in_date=check_in_date,
                    check_out_date=check_out_date,
                    adults=adults,
                    children=children,
                    rooms=rooms,
                    currency=currency,
                    country=country,
                    language=language,
                    max_results=max_results
                )
                return {"success": True, "data": result}
            except Exception as e:
                return {"success": False, "error": str(e)}
        
        @app.get("/hotel-details/{search_id}")
        async def api_get_hotel_details(search_id: str):
            """Get detailed hotel information"""
            try:
                result = get_hotel_details(search_id)
                return {"success": True, "data": result}
            except Exception as e:
                return {"success": False, "error": str(e)}
        
        print("✓ Successfully integrated hotel search tools")
        
    except Exception as e:
        print(f"Warning: Could not integrate hotel search tools: {e}")
    
    # Weather Integration
    try:
        from weatherstack_server import get_current_weather, get_weather_forecast
        
        @app.get("/weather/current")
        async def api_get_current_weather(
            location: str,
            units: str = "m"
        ):
            """Get current weather for a location"""
            try:
                result = get_current_weather(location=location, units=units)
                return {"success": True, "data": result}
            except Exception as e:
                return {"success": False, "error": str(e)}
        
        @app.get("/weather/forecast")
        async def api_get_weather_forecast(
            location: str,
            forecast_days: int = 3,
            hourly: bool = False,
            units: str = "m"
        ):
            """Get weather forecast for a location"""
            try:
                result = get_weather_forecast(
                    location=location,
                    forecast_days=forecast_days,
                    hourly=hourly,
                    units=units
                )
                return {"success": True, "data": result}
            except Exception as e:
                return {"success": False, "error": str(e)}
        
        print("✓ Successfully integrated weather tools")
        
    except Exception as e:
        print(f"Warning: Could not integrate weather tools: {e}")
    
    # Event Search Integration
    try:
        from event_server import search_events, get_event_details
        
        @app.post("/search-events")
        async def api_search_events(
            query: str,
            location: str = None,
            date_range_start: str = None,
            date_range_end: str = None,
            category: str = None,
            max_results: int = 10
        ):
            """Search for events"""
            try:
                result = search_events(
                    query=query,
                    location=location,
                    date_range_start=date_range_start,
                    date_range_end=date_range_end,
                    category=category,
                    max_results=max_results
                )
                return {"success": True, "data": result}
            except Exception as e:
                return {"success": False, "error": str(e)}
        
        @app.get("/event-details/{search_id}")
        async def api_get_event_details(search_id: str):
            """Get detailed event information"""
            try:
                result = get_event_details(search_id)
                return {"success": True, "data": result}
            except Exception as e:
                return {"success": False, "error": str(e)}
        
        print("✓ Successfully integrated event search tools")
        
    except Exception as e:
        print(f"Warning: Could not integrate event search tools: {e}")
    
    # Finance Integration
    try:
        from finance_server import convert_currency, lookup_stock
        
        @app.get("/finance/convert-currency")
        async def api_convert_currency(
            from_currency: str,
            to_currency: str,
            amount: float = 1.0
        ):
            """Convert currency"""
            try:
                result = convert_currency(
                    from_currency=from_currency,
                    to_currency=to_currency,
                    amount=amount
                )
                return {"success": True, "data": result}
            except Exception as e:
                return {"success": False, "error": str(e)}
        
        @app.get("/finance/stock/{symbol}")
        async def api_lookup_stock(symbol: str):
            """Look up stock information"""
            try:
                result = lookup_stock(symbol=symbol)
                return {"success": True, "data": result}
            except Exception as e:
                return {"success": False, "error": str(e)}
        
        print("✓ Successfully integrated finance tools")
        
    except Exception as e:
        print(f"Warning: Could not integrate finance tools: {e}")
    
    # Geocoding Integration
    try:
        from geocoder_server import geocode_location, reverse_geocode, calculate_distance
        
        @app.get("/geocoding/geocode")
        async def api_geocode_location(
            location: str,
            max_results: int = 1
        ):
            """Geocode a location to get coordinates"""
            try:
                result = geocode_location(
                    location=location,
                    max_results=max_results
                )
                return {"success": True, "data": result}
            except Exception as e:
                return {"success": False, "error": str(e)}
        
        @app.get("/geocoding/reverse")
        async def api_reverse_geocode(
            latitude: float,
            longitude: float
        ):
            """Reverse geocode coordinates to get location"""
            try:
                result = reverse_geocode(
                    latitude=latitude,
                    longitude=longitude
                )
                return {"success": True, "data": result}
            except Exception as e:
                return {"success": False, "error": str(e)}
        
        @app.get("/geocoding/distance")
        async def api_calculate_distance(
            lat1: float,
            lon1: float,
            lat2: float,
            lon2: float,
            unit: str = "km"
        ):
            """Calculate distance between two coordinates"""
            try:
                result = calculate_distance(
                    lat1=lat1,
                    lon1=lon1,
                    lat2=lat2,
                    lon2=lon2,
                    unit=unit
                )
                return {"success": True, "data": result}
            except Exception as e:
                return {"success": False, "error": str(e)}
        
        print("✓ Successfully integrated geocoding tools")
        
    except Exception as e:
        print(f"Warning: Could not integrate geocoding tools: {e}")
    
    # Add MCP Protocol Support for Claude API Integration
    @app.post("/sse")
    async def mcp_sse_endpoint(request: Request):
        """MCP Server-Sent Events endpoint for Claude API integration"""
        
        async def generate_mcp_events():
            # Send initial connection event
            yield {
                "event": "connected",
                "data": json.dumps({
                    "type": "server_info",
                    "server_name": "travel-assistant",
                    "version": "1.0.0",
                    "capabilities": {
                        "tools": True,
                        "resources": False,
                        "prompts": False
                    }
                })
            }
            
            # Send available tools
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
            
            yield {
                "event": "tools",
                "data": json.dumps({
                    "type": "tools_list",
                    "tools": tools
                })
            }
            
            # Keep connection alive and handle tool calls
            while True:
                try:
                    await asyncio.sleep(1)
                    yield {
                        "event": "heartbeat",
                        "data": json.dumps({"type": "ping", "timestamp": asyncio.get_event_loop().time()})
                    }
                except asyncio.CancelledError:
                    break
                except Exception as e:
                    yield {
                        "event": "error",
                        "data": json.dumps({"type": "error", "message": str(e)})
                    }
                    break
        
        return EventSourceResponse(
            generate_mcp_events(),
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "*",
            }
        )
    
    # Add MCP tool execution endpoint
    @app.post("/mcp/tool")
    async def mcp_tool_execution(request: Request):
        """Execute MCP tools for Claude API integration"""
        try:
            data = await request.json()
            tool_name = data.get("name")
            tool_input = data.get("input", {})
            
            # Route to appropriate tool function
            if tool_name == "search_flights":
                from flight_server import search_flights
                result = search_flights(**tool_input)
                return {"success": True, "result": result}
            
            elif tool_name == "search_hotels":
                from hotel_server import search_hotels
                result = search_hotels(**tool_input)
                return {"success": True, "result": result}
            
            elif tool_name == "get_current_weather":
                from weatherstack_server import get_current_weather
                result = get_current_weather(**tool_input)
                return {"success": True, "result": result}
            
            elif tool_name == "search_events":
                from event_server import search_events
                result = search_events(**tool_input)
                return {"success": True, "result": result}
            
            elif tool_name == "convert_currency":
                from finance_server import convert_currency
                result = convert_currency(**tool_input)
                return {"success": True, "result": result}
            
            elif tool_name == "geocode_location":
                from geocoder_server import geocode_location
                result = geocode_location(**tool_input)
                return {"success": True, "result": result}
            
            else:
                return {"success": False, "error": f"Unknown tool: {tool_name}"}
        
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    return app

def main():
    """Main entry point"""
    print("Travel Assistant MCP Server")
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
    print("API Documentation available at: /docs")
    
    # Start the server
    uvicorn.run(app, host=host, port=port)

if __name__ == "__main__":
    main()