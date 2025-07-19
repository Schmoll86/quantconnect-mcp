"""QuantConnect MCP Server Core Configuration"""

import os
from typing import Optional
from fastmcp import FastMCP

from .tools import (
    register_quantbook_tools,
    register_data_tools,
    register_analysis_tools,
    register_portfolio_tools,
    register_universe_tools,
    register_auth_tools,
    register_project_tools,
    register_file_tools,
    register_backtest_tools,
)
from .resources import register_system_resources
from .auth import configure_auth


mcp: FastMCP = FastMCP(
    name="QuantConnect MCP Server",
    instructions="""
    This server provides comprehensive QuantConnect API functionality for:
    - Research environment operations with QuantBook
    - Historical data retrieval and analysis
    - Statistical analysis (PCA, cointegration, mean reversion)
    - Portfolio optimization and risk analysis
    - Universe selection and asset filtering
    - Alternative data integration

    Use the available tools to interact with QuantConnect's research capabilities.
    """,
    on_duplicate_tools="error",
    dependencies=[
        "pandas",
        "numpy",
        "scipy",
        "scikit-learn",
        "matplotlib",
        "seaborn",
        "arch",
        "statsmodels",
        "httpx",
    ],
)

def main():
    """Initialize and run the QuantConnect MCP server."""

    # Auto-configure authentication from environment variables if available
    user_id = os.getenv("QUANTCONNECT_USER_ID")
    api_token = os.getenv("QUANTCONNECT_API_TOKEN")
    organization_id = os.getenv("QUANTCONNECT_ORGANIZATION_ID")

    if user_id and api_token:
        try:
            print("🔐 Configuring QuantConnect authentication from environment...")
            configure_auth(user_id, api_token, organization_id)
            print("✅ Authentication configured successfully")
        except Exception as e:
            print(f"⚠️  Failed to configure authentication: {e}")
            print(
                "💡 You can configure authentication later using the configure_quantconnect_auth tool"
            )

    # Register all tool modules
    print("🔧 Registering QuantConnect tools...")
    register_auth_tools(mcp)
    register_project_tools(mcp)
    register_file_tools(mcp)
    register_backtest_tools(mcp)
    register_quantbook_tools(mcp)
    register_data_tools(mcp)
    register_analysis_tools(mcp)
    register_portfolio_tools(mcp)
    register_universe_tools(mcp)

    # Register resources
    print("📊 Registering system resources...")
    register_system_resources(mcp)

    print(f"✅ QuantConnect MCP Server initialized")

    # Determine transport method
    transport = os.getenv("MCP_TRANSPORT", "stdio")

    if transport == "streamable-http":
        host = os.getenv("MCP_HOST", "127.0.0.1")
        port = int(os.getenv("MCP_PORT", "8000"))
        print(f"🌐 Starting HTTP server on {host}:{port}")
        mcp.run(
            transport="streamable-http",
            host=host,
            port=port,
            path=os.getenv("MCP_PATH", "/mcp"),
        )
    elif transport == "stdio":
        print("📡 Starting STDIO transport")
        mcp.run()  # Default stdio transport
    else:
        print(f"🚀 Starting with {transport} transport")
        mcp.run(transport=transport)


if __name__ == "__main__":
    main()
