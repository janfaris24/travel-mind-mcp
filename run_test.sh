#!/bin/bash

echo "🚀 Setting up and running Travel MCP Server test..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install packages if needed
if ! pip show anthropic > /dev/null 2>&1; then
    echo "📥 Installing required packages..."
    pip install anthropic python-dotenv
fi

echo "🧪 Running MCP server test..."
python quick_test.py

echo "✅ Test completed!"