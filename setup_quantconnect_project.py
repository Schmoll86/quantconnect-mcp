#!/usr/bin/env python3
"""
Setup Second-Order Effects Trading System in QuantConnect
This script creates the project and uploads the algorithm
"""

import os
import sys
import asyncio
import httpx
from pathlib import Path

# Add the quantconnect_mcp module to path
sys.path.insert(0, '/Users/schmoll/Documents/GitHub/quantconnect-mcp')

from quantconnect_mcp.src.auth.quantconnect_auth import QuantConnectAuth
from quantconnect_mcp.src.tools.project_tools import (
    create_project, 
    read_project,
    compile_project
)
from quantconnect_mcp.src.tools.file_tools import create_file, update_file_content

# Set up authentication
os.environ['QUANTCONNECT_USER_ID'] = '388061'
os.environ['QUANTCONNECT_API_TOKEN'] = 'e574cead7d73e1535172727fb546dca754b0a879c33a847e0e08695d4fb433e2'
os.environ['QUANTCONNECT_ORGANIZATION_ID'] = '15de91db32c751751a6898c844fb6b0f'

async def setup_second_order_project():
    """Create and configure the second-order effects project"""
    
    print("🚀 Setting up Second-Order Effects Trading System in QuantConnect\n")
    
    # Initialize auth
    auth = QuantConnectAuth()
    
    # Step 1: Create the project
    print("1️⃣ Creating QuantConnect project...")
    project_name = "SecondOrderEffectsEngine"
    
    try:
        # Create project
        result = await create_project(
            name=project_name,
            language="Python"
        )
        
        if result['success']:
            project_id = result['projectId']
            print(f"   ✅ Project created: {project_name} (ID: {project_id})\n")
        else:
            # Project might already exist, try to find it
            projects = await read_project()
            for proj in projects.get('projects', []):
                if proj['name'] == project_name:
                    project_id = proj['projectId']
                    print(f"   ℹ️ Project already exists: {project_name} (ID: {project_id})\n")
                    break
    except Exception as e:
        print(f"   ❌ Error creating project: {e}")
        return
    
    # Step 2: Upload the algorithm
    print("2️⃣ Uploading second-order algorithm...")
    
    # Read the algorithm file
    algo_path = Path('/Users/schmoll/Documents/GitHub/quantconnect-mcp/second_order_algo.py')
    with open(algo_path, 'r') as f:
        algo_content = f.read()
    
    try:
        # Create main.py file
        result = await create_file(
            project_id=project_id,
            name="main.py",
            content=algo_content
        )
        print(f"   ✅ Algorithm uploaded to main.py\n")
    except:
        # File might exist, update it
        result = await update_file_content(
            project_id=project_id,
            name="main.py",
            content=algo_content
        )
        print(f"   ✅ Algorithm updated in main.py\n")
    
    # Step 3: Create helper files
    print("3️⃣ Creating helper modules...")
    
    # Create supply chain mapper
    supply_chain_content = '''# Supply Chain and Relationship Mapper
import json
from typing import Dict, List, Set

class SupplyChainMapper:
    """Maps company relationships for second-order effect detection"""
    
    def __init__(self):
        # Extended supply chain database
        self.relationships = {
            # Tech Giants
            "AAPL": {
                "suppliers": ["QCOM", "SWKS", "AVGO", "QRVO", "TSM", "HON", "STX"],
                "customers": ["VZ", "T", "TMUS"],
                "competitors": ["GOOGL", "MSFT", "SSNLF"],
                "ecosystem": ["UBER", "LYFT", "SQ", "SHOP"]
            },
            
            # Electric Vehicles
            "TSLA": {
                "suppliers": ["PANW", "ALB", "LAC", "LTHM", "NVDA", "STM"],
                "competitors": ["F", "GM", "RIVN", "LCID", "NIO", "XPEV"],
                "infrastructure": ["CHPT", "BLNK", "EVGO"],
                "battery": ["QS", "SLDP", "MVST"]
            },
            
            # Semiconductors
            "NVDA": {
                "suppliers": ["TSM", "ASML", "AMAT", "LRCX", "KLAC"],
                "customers": ["MSFT", "GOOGL", "AMZN", "META", "TSLA"],
                "competitors": ["AMD", "INTC", "QCOM"],
                "related": ["SMCI", "DELL", "HPE"]
            },
            
            # Cloud/AI
            "MSFT": {
                "partners": ["NVDA", "AMD", "ORCL"],
                "competitors": ["AMZN", "GOOGL", "CRM"],
                "ecosystem": ["ADBE", "NOW", "TEAM", "DOCU"],
                "hardware": ["DELL", "HPQ", "NTAP"]
            }
        }
    
    def get_affected_tickers(self, primary_ticker: str, event_type: str) -> Dict[str, List[str]]:
        """Get all tickers affected by an event on the primary ticker"""
        
        if primary_ticker not in self.relationships:
            return {}
        
        affected = {}
        base_relations = self.relationships[primary_ticker]
        
        # Determine impact based on event type
        if "earnings_beat" in event_type.lower():
            affected["positive"] = base_relations.get("suppliers", [])
            affected["negative"] = base_relations.get("competitors", [])
            
        elif "supply_disruption" in event_type.lower():
            affected["negative"] = base_relations.get("customers", [])
            affected["positive"] = base_relations.get("competitors", [])
            
        elif "innovation" in event_type.lower():
            affected["positive"] = base_relations.get("ecosystem", [])
            affected["negative"] = base_relations.get("competitors", [])
        
        return affected
    
    def calculate_impact_score(self, primary_ticker: str, affected_ticker: str, 
                              relationship_type: str) -> float:
        """Calculate the expected impact magnitude (0-1)"""
        
        # Impact weights by relationship type
        weights = {
            "suppliers": 0.7,
            "customers": 0.6,
            "competitors": 0.5,
            "ecosystem": 0.4,
            "infrastructure": 0.6,
            "partners": 0.8
        }
        
        return weights.get(relationship_type, 0.3)
'''
    
    try:
        result = await create_file(
            project_id=project_id,
            name="supply_chain_mapper.py",
            content=supply_chain_content
        )
        print(f"   ✅ Created supply_chain_mapper.py\n")
    except:
        result = await update_file_content(
            project_id=project_id,
            name="supply_chain_mapper.py",
            content=supply_chain_content
        )
        print(f"   ✅ Updated supply_chain_mapper.py\n")
    
    # Step 4: Compile the project
    print("4️⃣ Compiling project...")
    try:
        compile_result = await compile_project(project_id=project_id)
        if compile_result.get('success'):
            print(f"   ✅ Project compiled successfully!\n")
            print(f"   Compile ID: {compile_result.get('compileId')}")
        else:
            print(f"   ⚠️ Compilation had issues: {compile_result}")
    except Exception as e:
        print(f"   ❌ Compilation error: {e}")
    
    print("\n✨ Setup complete! Next steps:")
    print("   1. Go to QuantConnect.com and open your project")
    print(f"   2. Project name: {project_name}")
    print("   3. Run a backtest to see second-order effects in action")
    print("   4. Connect your IBKR/Alpaca accounts for live trading")
    
    return project_id

if __name__ == "__main__":
    # Run the setup
    asyncio.run(setup_second_order_project())
