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

# Add all server directories to Python path
current_dir = Path(__file__).parent
for server_dir in current_dir.iterdir():
    if server_dir.is_dir() and (server_dir / "main.py").exists():
        sys.path.append(str(server_dir))

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
    
    # Import and start the primary flight search server
    try:
        from flight_search.flight_server import mcp
        import uvicorn
        
        # Get port from environment variable (Render provides PORT)
        port = int(os.getenv("PORT", 8000))
        host = "0.0.0.0"
        
        print(f"Starting server on {host}:{port}")
        
        # Create ASGI app from FastMCP
        app = mcp.create_app()
        
        # Start the server
        uvicorn.run(app, host=host, port=port)
        
    except ImportError as e:
        print(f"Error importing flight server: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error starting server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()