#!/usr/bin/env python3
"""
Direct QuantConnect API setup for Second-Order Effects Trading System
"""

import httpx
import json
import time
from hashlib import sha256
from base64 import b64encode

# Your credentials
USER_ID = "388061"
API_TOKEN = "e574cead7d73e1535172727fb546dca754b0a879c33a847e0e08695d4fb433e2"
ORGANIZATION_ID = "15de91db32c751751a6898c844fb6b0f"
BASE_URL = "https://www.quantconnect.com/api/v2/"

def get_auth_headers():
    """Generate authenticated headers for QuantConnect API"""
    timestamp = str(int(time.time()))
    time_stamped_token = f"{API_TOKEN}:{timestamp}".encode("utf-8")
    hashed_token = sha256(time_stamped_token).hexdigest()
    authentication = f"{USER_ID}:{hashed_token}"
    encoded_auth = b64encode(authentication.encode("utf-8")).decode("ascii")
    
    return {
        "Authorization": f"Basic {encoded_auth}",
        "Timestamp": timestamp
    }

def create_project(name, language="Py"):
    """Create a new QuantConnect project"""
    url = f"{BASE_URL}projects/create"
    headers = get_auth_headers()
    headers["Content-Type"] = "application/json"
    
    data = {
        "name": name,
        "language": language,
        "organizationId": ORGANIZATION_ID
    }
    
    response = httpx.post(url, headers=headers, json=data)
    return response.json()

def create_file(project_id, filename, content):
    """Create a file in the project"""
    url = f"{BASE_URL}files/create"
    headers = get_auth_headers()
    headers["Content-Type"] = "application/json"
    
    data = {
        "projectId": project_id,
        "name": filename,
        "content": content
    }
    
    response = httpx.post(url, headers=headers, json=data)
    return response.json()

def compile_project(project_id):
    """Compile the project"""
    url = f"{BASE_URL}compile/create"
    headers = get_auth_headers()
    headers["Content-Type"] = "application/json"
    
    data = {"projectId": project_id}
    
    response = httpx.post(url, headers=headers, json=data)
    return response.json()

def main():
    print("🚀 Setting up Second-Order Effects Trading System in QuantConnect\n")
    
    # Step 1: Create project
    print("1️⃣ Creating project...")
    project_name = "SecondOrderEffectsEngine"
    
    result = create_project(project_name)
    
    if result.get('success'):
        project_id = result['projects'][0]['projectId']
        print(f"   ✅ Project created: {project_name} (ID: {project_id})\n")
    else:
        print(f"   ❌ Error: {result.get('errors', result)}")
        return
    
    # Step 2: Read and upload the algorithm
    print("2️⃣ Uploading algorithm...")
    
    with open('second_order_algo.py', 'r') as f:
        algo_content = f.read()
    
    file_result = create_file(project_id, "main.py", algo_content)
    
    if file_result.get('success'):
        print(f"   ✅ Algorithm uploaded successfully!\n")
    else:
        print(f"   ❌ Error: {file_result}")
    
    # Step 3: Compile
    print("3️⃣ Compiling project...")
    compile_result = compile_project(project_id)
    
    if compile_result.get('success'):
        print(f"   ✅ Compilation successful!\n")
        print(f"   Compile ID: {compile_result.get('compileId')}")
    else:
        print(f"   ⚠️ Compilation issues: {compile_result}")
    
    print("\n✨ Project setup complete!")
    print(f"   📊 Project URL: https://www.quantconnect.com/project/{project_id}")
    print("   🎯 Next: Run a backtest to see second-order effects in action!")

if __name__ == "__main__":
    main()
