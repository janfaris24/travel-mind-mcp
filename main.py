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
import uvicorn
from fastapi import FastAPI

# Add all server directories to Python path
current_dir = Path(__file__).parent
sys.path.append(str(current_dir / "flight-search"))
sys.path.append(str(current_dir / "hotel-search"))
sys.path.append(str(current_dir / "weather-search"))
sys.path.append(str(current_dir / "event-search"))
sys.path.append(str(current_dir / "finance-search"))
sys.path.append(str(current_dir / "geocoder"))

# Create FastAPI app directly
app = FastAPI(title="Travel Assistant MCP Server", version="1.0.0")

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
        "status": "running",
        "endpoints": {
            "/": "Service information",
            "/health": "Health check",
            "/flight-search": "Flight search service",
            "/hotel-search": "Hotel search service", 
            "/weather": "Weather service",
            "/events": "Event search service",
            "/finance": "Finance service",
            "/geocoding": "Geocoding service"
        }
    }

@app.get("/health")
async def health():
    return {"status": "healthy", "message": "Travel Assistant MCP Server is running"}

# Import individual servers to register their endpoints
def register_services():
    """Import and register all MCP services"""
    services_registered = []
    
    try:
        from flight_server import mcp as flight_mcp
        # Mount flight search at /flight-search
        flight_app = flight_mcp.create_app()  
        app.mount("/flight-search", flight_app)
        services_registered.append("flight-search")
        print("✓ Registered flight search service at /flight-search")
    except Exception as e:
        print(f"Warning: Could not register flight service: {e}")
    
    try:
        from hotel_server import mcp as hotel_mcp
        hotel_app = hotel_mcp.create_app()
        app.mount("/hotel-search", hotel_app)
        services_registered.append("hotel-search")
        print("✓ Registered hotel search service at /hotel-search")
    except Exception as e:
        print(f"Warning: Could not register hotel service: {e}")
    
    try:
        # Try weather_server first, then weatherstack_server
        try:
            from weather_server import mcp as weather_mcp
            weather_app = weather_mcp.create_app()
            app.mount("/weather", weather_app)
            print("✓ Registered weather service at /weather")
        except:
            from weatherstack_server import mcp as weather_mcp
            weather_app = weather_mcp.create_app()
            app.mount("/weather", weather_app)
            print("✓ Registered weatherstack service at /weather")
        services_registered.append("weather")
    except Exception as e:
        print(f"Warning: Could not register weather service: {e}")
    
    try:
        from event_server import mcp as event_mcp
        event_app = event_mcp.create_app()
        app.mount("/events", event_app)
        services_registered.append("events")
        print("✓ Registered event search service at /events")
    except Exception as e:
        print(f"Warning: Could not register event service: {e}")
    
    try:
        # Try finance_server first, then finance_search_server
        try:
            from finance_server import mcp as finance_mcp
            finance_app = finance_mcp.create_app()
            app.mount("/finance", finance_app)
            print("✓ Registered finance service at /finance")
        except:
            from finance_search_server import mcp as finance_mcp
            finance_app = finance_mcp.create_app()
            app.mount("/finance", finance_app)
            print("✓ Registered finance search service at /finance")
        services_registered.append("finance")
    except Exception as e:
        print(f"Warning: Could not register finance service: {e}")
    
    try:
        from geocoder_server import mcp as geocoder_mcp
        geocoder_app = geocoder_mcp.create_app()
        app.mount("/geocoding", geocoder_app)
        services_registered.append("geocoding")
        print("✓ Registered geocoding service at /geocoding")
    except Exception as e:
        print(f"Warning: Could not register geocoding service: {e}")
    
    return services_registered

def main():
    """Main entry point for the travel assistant MCP server"""
    print("Travel Assistant MCP Server")
    print("Registering services...")
    
    services = register_services()
    
    print(f"\n✓ Successfully registered {len(services)} services:")
    for service in services:
        print(f"  - {service}")
    
    print("\nAvailable endpoints:")
    print("- GET /: Service information")
    print("- GET /health: Health check")
    for service in services:
        print(f"- /{service}: {service.replace('-', ' ').title()} service")
    
    # Get port from environment variable (Render provides PORT)
    port = int(os.getenv("PORT", 8000))
    host = "0.0.0.0"
    
    print(f"\nStarting server on {host}:{port}")
    
    # Start the server
    uvicorn.run(app, host=host, port=port)

if __name__ == "__main__":
    main()