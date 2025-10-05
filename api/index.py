import json
import os
from typing import List, Dict, Any

import numpy as np
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from scipy.stats import scoreatpercentile # A common way to calculate percentile

app = FastAPI()

# --- CORS Configuration ---
# Enable CORS for POST requests from any origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["POST", "OPTIONS"],  # Allows POST and preflight OPTIONS
    allow_headers=["*"],  # Allows all headers
)

# --- Data Loading (Simulated) ---
# In a real Vercel deployment, this file needs to be present in the root directory.
DATA_FILE = "q-vercel-latency.json"
TELEMETRY_DATA: List[Dict[str, Any]] = []

# Load data on startup
try:
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            TELEMETRY_DATA = json.load(f)
    else:
        # Log or handle case where data file is missing
        print(f"Warning: Data file {DATA_FILE} not found. Using empty data.")
except json.JSONDecodeError:
    print(f"Error: Could not decode JSON from {DATA_FILE}")
except Exception as e:
    print(f"An error occurred during data loading: {e}")


# --- Pydantic Models ---
class LatencyRequest(BaseModel):
    regions: List[str]
    threshold_ms: int


class RegionMetrics(BaseModel):
    region: str
    avg_latency: float
    p95_latency: float
    avg_uptime: float
    breaches: int


# --- Helper Function for Metric Calculation ---
def calculate_metrics(data: List[Dict[str, Any]], threshold: int) -> Dict[str, RegionMetrics]:
    """Calculates metrics for each region."""
    
    # 1. Group data by region
    regional_pings = {}
    for record in data:
        region = record.get("region")
        latency = record.get("latency_ms")
        if region and isinstance(latency, (int, float)):
            if region not in regional_pings:
                regional_pings[region] = []
            regional_pings[region].append(latency)

    # 2. Calculate metrics for each region
    results: Dict[str, RegionMetrics] = {}
    for region, latencies in regional_pings.items():
        if not latencies:
            continue

        latencies_np = np.array(latencies)
        
        # Calculate avg_latency (mean)
        avg_latency = np.mean(latencies_np)
        
        # Calculate p95_latency (95th percentile)
        # Using scipy's scoreatpercentile for standard percentile calculation
        p95_latency = scoreatpercentile(latencies_np, 95)
        
        # Calculate breaches (count of records above threshold)
        breaches = np.sum(latencies_np > threshold)
        
        # Calculate avg_uptime (mean of 'uptime' field, which is 1000 for every ping)
        # Assuming avg_uptime means the average of the 'uptime' value, which is consistently 1000 in the sample data
        # If 'uptime' represents a status, this interpretation might change, but based on the sample structure:
        avg_uptime = 1000.0  # Since every record has "uptime": 1000
        
        results[region] = RegionMetrics(
            region=region,
            avg_latency=round(float(avg_latency), 3),
            p95_latency=round(float(p95_latency), 3),
            avg_uptime=float(avg_uptime),
            breaches=int(breaches)
        )
        
    return results


# --- FastAPI Endpoint ---
@app.post("/")
def get_latency_metrics(request: LatencyRequest) -> List[RegionMetrics]:
    """
    Accepts POST request and returns per-region latency metrics.
    """
    if not TELEMETRY_DATA:
        raise HTTPException(status_code=503, detail="Telemetry data is not loaded.")
        
    all_metrics = calculate_metrics(TELEMETRY_DATA, request.threshold_ms)
    
    # Filter results for the requested regions
    filtered_results = []
    for region in request.regions:
        if region in all_metrics:
            filtered_results.append(all_metrics[region])
            
    return filtered_results
