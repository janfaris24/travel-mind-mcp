#!/usr/bin/env python3
"""
Quick test for Claude API with MCP server
"""

import os
from dotenv import load_dotenv
import anthropic

# Load environment variables
load_dotenv()

def test_basic_connection():
    """Quick test of Claude API with MCP server"""
    try:
        client = anthropic.Anthropic()
        
        print("🧪 Testing Claude API + MCP Server connection...")
        print("🌐 MCP Server: https://travel-mind-mcp.onrender.com/sse")
        
        response = client.beta.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=300,
            messages=[
                {
                    "role": "user",
                    "content": "Hello! What travel tools do you have available?"
                }
            ],
            mcp_servers=[
                {
                    "type": "url",
                    "url": "https://travel-mind-mcp.onrender.com/sse",
                    "name": "travel-assistant"
                }
            ],
            betas=["mcp-client-2025-04-04"]
        )
        
        print("✅ SUCCESS! Claude connected to your MCP server!")
        print("\n📝 Response:")
        print("-" * 50)
        
        for content in response.content:
            if hasattr(content, 'text'):
                print(content.text)
        
        print("-" * 50)
        print(f"📊 Tokens used - Input: {response.usage.input_tokens}, Output: {response.usage.output_tokens}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_basic_connection()
    
    if success:
        print("\n🎉 Your MCP server is working with Claude API!")
        print("🔗 You can now use it for travel assistance!")
    else:
        print("\n🚨 Connection failed. Check your setup.")