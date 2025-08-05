#!/bin/bash

# QuantConnect MCP Server Startup Script

echo "🚀 Starting QuantConnect MCP Server..."
echo ""

# Navigate to project directory
cd /Users/schmoll/Documents/GitHub/quantconnect-mcp

# Load environment variables from .env file
export $(grep -v '^#' .env | xargs)

# Activate virtual environment
source .venv/bin/activate

# Display configuration
echo "📊 Configuration:"
echo "   User ID: $QUANTCONNECT_USER_ID"
echo "   Organization ID: $QUANTCONNECT_ORGANIZATION_ID"
echo "   Transport: $MCP_TRANSPORT"
echo ""

# Run the server
echo "✨ Server starting on $MCP_TRANSPORT transport..."
echo "   Press Ctrl+C to stop the server"
echo ""

python -m quantconnect_mcp.main
