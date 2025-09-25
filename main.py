#!/usr/bin/env python3
"""
Travel Assistant MCP Server
A comprehensive MCP server providing travel-related services including:
- Flight search and other travel services
"""

import os
import sys
from pathlib import Path
import uvicorn
from fastapi import FastAPI

# Add flight search to path
current_dir = Path(__file__).parent
sys.path.append(str(current_dir / "flight-search"))

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
            "services": ["flight-search"],
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
        
        @app.get("/error")
        async def error_info():
            return {"error": f"Flight search service unavailable: {str(e)}"}
    
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