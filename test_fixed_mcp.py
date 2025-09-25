#!/usr/bin/env python3
"""
Test the fixed MCP protocol implementation
"""

import os
from dotenv import load_dotenv
import anthropic

# Load environment variables
load_dotenv()

def test_fixed_mcp():
    """Test Claude API with fixed MCP server"""
    try:
        client = anthropic.Anthropic()
        
        print("🧪 Testing FIXED MCP Protocol...")
        print("🌐 Server: https://travel-mind-mcp.onrender.com/sse")
        print("📋 Protocol: MCP 2024-11-05 with JSON-RPC 2.0")
        
        response = client.beta.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=400,
            messages=[
                {
                    "role": "user",
                    "content": "Hello! What travel tools do you have available? Can you list them for me?"
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
        
        print("✅ SUCCESS! Fixed MCP protocol works!")
        print("\n📝 Claude Response:")
        print("-" * 50)
        
        for content in response.content:
            if hasattr(content, 'text'):
                print(content.text)
            elif hasattr(content, 'type'):
                if content.type == 'mcp_tool_use':
                    print(f"🔧 Tool used: {content.name}")
                elif content.type == 'mcp_tool_result':
                    print(f"✅ Tool result received")
        
        print("-" * 50)
        print(f"📊 Tokens: {response.usage.input_tokens} in, {response.usage.output_tokens} out")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 Testing Fixed MCP Implementation")
    print("=" * 50)
    
    success = test_fixed_mcp()
    
    if success:
        print("\n🎉 FIXED! Your MCP server now works with Claude API!")
        print("🔧 Ready for tool testing!")
    else:
        print("\n🚨 Still having issues. Check the implementation.")