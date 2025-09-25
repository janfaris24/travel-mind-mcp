#!/usr/bin/env python3
"""
Travel Assistant MCP Server
A comprehensive MCP server providing travel-related services including:
- Flight search
- Hotel search  
- Weather information
- Event search
- Finance/currency data
- Geocoding services
"""

import os
import sys
from pathlib import Path
import asyncio
import uvicorn
from fastapi import FastAPI
from mcp.server.fastmcp import FastMCP

# Add all server directories to Python path
current_dir = Path(__file__).parent
sys.path.append(str(current_dir / "flight-search"))
sys.path.append(str(current_dir / "hotel-search"))
sys.path.append(str(current_dir / "weather-search"))
sys.path.append(str(current_dir / "event-search"))
sys.path.append(str(current_dir / "finance-search"))
sys.path.append(str(current_dir / "geocoder"))

# Create main FastMCP instance
main_mcp = FastMCP("travel-assistant")

# Import and register tools from all servers
def register_all_tools():
    """Register tools from all MCP servers"""
    try:
        # Flight search tools
        from flight_server import search_flights
        main_mcp.tool()(search_flights)
        print("✓ Registered flight search tools")
    except Exception as e:
        print(f"Warning: Could not register flight tools: {e}")
    
    try:
        # Hotel search tools
        from hotel_server import search_hotels
        main_mcp.tool()(search_hotels)
        print("✓ Registered hotel search tools")
    except Exception as e:
        print(f"Warning: Could not register hotel tools: {e}")
    
    try:
        # Weather tools
        from weather_server import get_weather
        main_mcp.tool()(get_weather)
        print("✓ Registered weather tools")
    except Exception as e:
        print(f"Warning: Could not register weather tools: {e}")
    
    try:
        # Event search tools
        from event_server import search_events
        main_mcp.tool()(search_events)
        print("✓ Registered event search tools")
    except Exception as e:
        print(f"Warning: Could not register event tools: {e}")
    
    try:
        # Finance tools
        from finance_server import get_currency_rate
        main_mcp.tool()(get_currency_rate)
        print("✓ Registered finance tools")
    except Exception as e:
        print(f"Warning: Could not register finance tools: {e}")
    
    try:
        # Geocoder tools
        from geocoder_server import geocode_location
        main_mcp.tool()(geocode_location)
        print("✓ Registered geocoder tools")
    except Exception as e:
        print(f"Warning: Could not register geocoder tools: {e}")

# Register all tools
register_all_tools()

# Create the FastAPI app
app = main_mcp.create_app()

@app.get("/")
async def root():
    return {
        "message": "Travel Assistant MCP Server",
        "version": "1.0.0",
        "services": [
            "flight-search",
            "hotel-search", 
            "weather",
            "events",
            "finance",
            "geocoding"
        ],
        "status": "running"
    }

@app.get("/health")
async def health():
    return {"status": "healthy"}

def main():
    """Main entry point for the travel assistant MCP server"""
    print("Travel Assistant MCP Server")
    print("Available services:")
    print("- Flight Search")
    print("- Hotel Search")
    print("- Weather Information") 
    print("- Event Search")
    print("- Finance/Currency Data")
    print("- Geocoding Services")
    
    # Get port from environment variable (Render provides PORT)
    port = int(os.getenv("PORT", 8000))
    host = "0.0.0.0"
    
    print(f"Starting server on {host}:{port}")
    
    # Start the server
    uvicorn.run(app, host=host, port=port)

if __name__ == "__main__":
    main()