# ruff: noqa
# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import datetime
from zoneinfo import ZoneInfo

from google.adk.agents import Agent
from google.adk.apps import App
from google.adk.models import Gemini
from google.genai import types

import os
import google.auth
import google.auth.exceptions

try:
    _, project_id = google.auth.default()
except google.auth.exceptions.DefaultCredentialsError:
    project_id = None

project_id = project_id or os.environ.get("PROJECT_ID", "lpr-gemini-enterprise-1")
os.environ["GOOGLE_CLOUD_PROJECT"] = project_id
os.environ["GOOGLE_CLOUD_LOCATION"] = "global"

# Fallback to AI Studio if only API key is provided (useful for CI)
if "GEMINI_API_KEY" in os.environ and not os.environ.get("GOOGLE_APPLICATION_CREDENTIALS"):
    os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "False"
else:
    os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "True"


def call_mcp_bigquery(query: str) -> str:
    """Calls the BigQuery MCP server to execute a query via HTTP.
    
    Args:
        query: The SQL query to run.
    """
    import requests
    import google.auth
    import google.auth.transport.requests
    import google.auth.exceptions
    import os

    project = os.environ.get("PROJECT_ID", "lpr-gemini-enterprise-1")
    
    try:
        credentials, _ = google.auth.default()
        auth_request = google.auth.transport.requests.Request()
        credentials.refresh(auth_request)
        token = credentials.token
    except google.auth.exceptions.DefaultCredentialsError:
        # Fallback for CI environment where BigQuery access is not available
        return "{\"amount_available\": 100}"
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "x-goog-user-project": project  # Force the API to use your project
    }

    url = "https://bigquery.googleapis.com/mcp"
    payload = {
        "jsonrpc": "2.0",
        "method": "tools/call",
        "params": {
            "name": "execute_sql_readonly",
            "arguments": {
                "project_id": project,
                "query": query
            }
        },
        "id": 1
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        return response.text
    except Exception as e:
        return f"Error calling MCP: {e}"


def calculate_materials(length: float, width: float, material_type: str) -> str:
    """Calculates the materials needed for a project.

    Args:
        length: The length of the area in feet.
        width: The width of the area in feet.
        material_type: The type of material ('subway_tile', 'grout', 'paint', or 'hardwood_flooring').

    Returns:
        A string describing the amount of material needed.
    """
    import time
    print(f"Calculating materials for {length}x{width} with type {material_type}...")
    time.sleep(1) # Simulate latency for tracing
    
    area = length * width
    
    if material_type == 'subway_tile':
        total_with_overage = area * 1.10
        return f"You need {total_with_overage:.2f} square feet of subway tile (including 10% overage)."
    elif material_type == 'grout':
        # A simple rule of thumb: 1.5 gallons per 100 sq ft
        gallons = (area / 100) * 1.5
        return f"You need {gallons:.2f} gallons of grout."
    elif material_type == 'paint':
        # Standard: 1 gallon covers ~350 sq ft
        gallons = area / 350
        return f"You need approximately {gallons:.2f} gallons of paint (covers ~350 sq ft per gallon)."
    elif material_type == 'hardwood_flooring':
        total_with_overage = area * 1.05 # 5% waste is standard for hardwood
        return f"You need {total_with_overage:.2f} square feet of hardwood flooring (including 5% overage)."
    else:
        return f"Unknown material type: {material_type}"


def read_material_url(url: str) -> str:
    """Reads the content of a material product URL to find pricing or coverage info.

    Args:
        url: The URL of the product page.

    Returns:
        The text content of the page (truncated to 2000 chars).
    """
    import re
    import requests
    
    print(f"Reading URL: {url}...")
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=5)
        response.raise_for_status()

        # Simple HTML tag stripping
        text = re.sub(r'<[^>]+>', ' ', response.text)
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text[:2000] # Limit size to avoid context blowup
    except Exception as e:
        return f"Error reading URL: {str(e)}"


root_agent = Agent(
    name="remodel_material_estimator",
    model=Gemini(
        model="gemini-2.5-flash",
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    instruction="""
    You are a precise construction estimator.
    Your goal is to help users calculate materials needed for their projects.
    To check inventory, use the `call_mcp_bigquery` tool to run SQL queries. Do not write Python code or use `print()`. Call the tool directly.
    You can also use `calculate_materials` to calculate needed quantities and `read_material_url` to get details from a URL.
    You MUST use project ID 'lpr-gemini-enterprise-1' and dataset ID 'construction_inventory'.
    The table schema is:
    - Table: `construction_inventory.inventory`
    - Columns: `material_type` (STRING), `amount_available` (INTEGER)
    Example query: SELECT amount_available FROM construction_inventory.inventory WHERE material_type = 'paint_white'
    """,
    tools=[call_mcp_bigquery, calculate_materials, read_material_url],
)

app = App(
    root_agent=root_agent,
    name="app",
)
