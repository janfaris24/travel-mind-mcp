# Travel Assistant MCP Server

A comprehensive Model Context Protocol (MCP) server providing travel-related services including flight search, hotel search, weather information, event search, finance/currency data, and geocoding services.

## Features

- **Flight Search**: Search for flights using SerpAPI's Google Flights API
- **Hotel Search**: Find hotels and accommodations
- **Weather Information**: Get current weather data
- **Event Search**: Find events and conferences
- **Finance/Currency**: Get currency exchange rates
- **Geocoding**: Convert addresses to coordinates and vice versa

## Deployment to Render

### Prerequisites

1. A GitHub account with this repository
2. A Render account (render.com)
3. API keys for services (SerpAPI, WeatherStack, etc.)

### Deployment Steps

1. **Connect to Render:**
   - Go to render.com and sign up/login
   - Click "New +" and select "Web Service"
   - Connect your GitHub account and select this repository

2. **Configure Environment Variables:**
   - Add the following environment variables in Render:
     - `SERPAPI_KEY`: Your SerpAPI key for flight searches
     - `WEATHERSTACK_KEY`: Your WeatherStack API key for weather data
     - `PORT`: Will be automatically set by Render

3. **Deploy:**
   - Render will automatically build and deploy using the settings in `render.yaml`
   - The service will be available at your Render URL

## Using as Remote MCP Server

Once deployed, you can use this as a remote MCP server:

1. **Get your Render URL** (e.g., `https://travel-assistant-mcp.onrender.com`)

2. **Configure in Claude or other MCP clients:**
   ```json
   {
     "mcpServers": {
       "travel-assistant": {
         "command": "mcp",
         "args": ["--transport", "http", "--url", "https://your-render-url.onrender.com"]
       }
     }
   }
   ```

3. **Available endpoints:**
   - `GET /`: Service information
   - `GET /health`: Health check
   - `POST /mcp`: MCP protocol endpoint

## Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export SERPAPI_KEY=your_key_here
export WEATHERSTACK_KEY=your_key_here

# Run the server
python main.py
```

## API Keys Required

- **SerpAPI**: For flight and travel searches
- **WeatherStack**: For weather information
- Additional keys may be required for specific services

## License

MIT License