import json
import numpy as np
from fastapi import FastAPI, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import os

app = FastAPI()

# Enable CORS to allow POST requests from any origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)




# Load telemetry data
def load_telemetry_data():
    try:
        # Try to load from the same directory as the script
        current_dir = os.path.dirname(os.path.abspath(_file_))
        json_path = os.path.join(os.path.dirname(current_dir), 'q-vercel-latency.json')
        
        with open(json_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        # Fallback: embedded data if file not found
        return [
            {"region": "apac", "service": "analytics", "latency_ms": 204.41, "uptime_pct": 98.045, "timestamp": 20250301},
            {"region": "apac", "service": "recommendations", "latency_ms": 209.81, "uptime_pct": 98.435, "timestamp": 20250302},
            {"region": "apac", "service": "recommendations", "latency_ms": 124.03, "uptime_pct": 98.549, "timestamp": 20250303},
            {"region": "apac", "service": "checkout", "latency_ms": 183.54, "uptime_pct": 98.469, "timestamp": 20250304},
            {"region": "apac", "service": "checkout", "latency_ms": 160.28, "uptime_pct": 98.456, "timestamp": 20250305},
            {"region": "apac", "service": "recommendations", "latency_ms": 213.61, "uptime_pct": 97.163, "timestamp": 20250306},
            {"region": "apac", "service": "checkout", "latency_ms": 207.13, "uptime_pct": 98.853, "timestamp": 20250307},
            {"region": "apac", "service": "checkout", "latency_ms": 168.95, "uptime_pct": 99.461, "timestamp": 20250308},
            {"region": "apac", "service": "checkout", "latency_ms": 142.97, "uptime_pct": 99.168, "timestamp": 20250309},
            {"region": "apac", "service": "support", "latency_ms": 128.06, "uptime_pct": 97.556, "timestamp": 20250310},
            {"region": "apac", "service": "payments", "latency_ms": 151, "uptime_pct": 98.723, "timestamp": 20250311},
            {"region": "apac", "service": "checkout", "latency_ms": 220.73, "uptime_pct": 97.275, "timestamp": 20250312},
            {"region": "emea", "service": "checkout", "latency_ms": 152.61, "uptime_pct": 97.698, "timestamp": 20250301},
            {"region": "emea", "service": "support", "latency_ms": 146.74, "uptime_pct": 98.74, "timestamp": 20250302},
            {"region": "emea", "service": "support", "latency_ms": 218.9, "uptime_pct": 98.367, "timestamp": 20250303},
            {"region": "emea", "service": "checkout", "latency_ms": 153.29, "uptime_pct": 97.742, "timestamp": 20250304},
            {"region": "emea", "service": "checkout", "latency_ms": 133.86, "uptime_pct": 97.88, "timestamp": 20250305},
            {"region": "emea", "service": "recommendations", "latency_ms": 212.59, "uptime_pct": 97.422, "timestamp": 20250306},
            {"region": "emea", "service": "recommendations", "latency_ms": 183.5, "uptime_pct": 99.306, "timestamp": 20250307},
            {"region": "emea", "service": "payments", "latency_ms": 129.48, "uptime_pct": 97.982, "timestamp": 20250308},
            {"region": "emea", "service": "payments", "latency_ms": 209.74, "uptime_pct": 97.868, "timestamp": 20250309},
            {"region": "emea", "service": "support", "latency_ms": 197.45, "uptime_pct": 97.459, "timestamp": 20250310},
            {"region": "emea", "service": "recommendations", "latency_ms": 201.87, "uptime_pct": 98.909, "timestamp": 20250311},
            {"region": "emea", "service": "catalog", "latency_ms": 202.21, "uptime_pct": 97.922, "timestamp": 20250312},
            {"region": "amer", "service": "catalog", "latency_ms": 163.76, "uptime_pct": 99.367, "timestamp": 20250301},
            {"region": "amer", "service": "analytics", "latency_ms": 213.54, "uptime_pct": 98.102, "timestamp": 20250302},
            {"region": "amer", "service": "catalog", "latency_ms": 145.12, "uptime_pct": 98.241, "timestamp": 20250303},
            {"region": "amer", "service": "checkout", "latency_ms": 150.38, "uptime_pct": 97.996, "timestamp": 20250304},
            {"region": "amer", "service": "support", "latency_ms": 216.51, "uptime_pct": 98.244, "timestamp": 20250305},
            {"region": "amer", "service": "analytics", "latency_ms": 232.17, "uptime_pct": 98.243, "timestamp": 20250306},
            {"region": "amer", "service": "checkout", "latency_ms": 115.72, "uptime_pct": 98.896, "timestamp": 20250307},
            {"region": "amer", "service": "support", "latency_ms": 171.96, "uptime_pct": 98.462, "timestamp": 20250308},
            {"region": "amer", "service": "recommendations", "latency_ms": 187.78, "uptime_pct": 98.857, "timestamp": 20250309},
            {"region": "amer", "service": "recommendations", "latency_ms": 124.95, "uptime_pct": 99.062, "timestamp": 20250310},
            {"region": "amer", "service": "catalog", "latency_ms": 171.63, "uptime_pct": 99.207, "timestamp": 20250311},
            {"region": "amer", "service": "payments", "latency_ms": 226.51, "uptime_pct": 98.832, "timestamp": 20250312}
        ]

# Load data once at startup
telemetry_data = load_telemetry_data()

class TelemetryRequest(BaseModel):
    regions: List[str]
    threshold_ms: float

class RegionMetrics(BaseModel):
    avg_latency: float
    p95_latency: float
    avg_uptime: float
    breaches: int

@app.get("/")
async def health_check():
    return "The health check is successful!"

@app.options("/")
@app.options("/telemetry")
async def handle_options(response: Response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "*"
    response.headers["Access-Control-Max-Age"] = "86400"
    return {"message": "OK"}

@app.post("/")
@app.post("/telemetry")
async def process_telemetry(request: TelemetryRequest, response: Response):
    # Explicitly set CORS headers
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "POST, GET, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    
    try:
        result = {}
        
        for region in request.regions:
            # Filter data for the specific region
            region_data = [record for record in telemetry_data if record["region"] == region]
            
            if not region_data:
                result[region] = {
                    "avg_latency": 0.0,
                    "p95_latency": 0.0,
                    "avg_uptime": 0.0,
                    "breaches": 0
                }
                continue
            
            # Extract latency and uptime values
            latencies = [record["latency_ms"] for record in region_data]
            uptimes = [record["uptime_pct"] for record in region_data]
            
            # Calculate metrics
            avg_latency = np.mean(latencies)
            p95_latency = np.percentile(latencies, 95)
            avg_uptime = np.mean(uptimes)
            breaches = sum(1 for latency in latencies if latency > request.threshold_ms)
            
            result[region] = {
                "avg_latency": round(avg_latency, 2),
                "p95_latency": round(p95_latency, 2),
                "avg_uptime": round(avg_uptime, 3),
                "breaches": breaches
            }
        
        # Create response ensuring all requested regions have stats
        response_data = {}
        
        # Add each requested region with its stats
        for region in request.regions:
            if region in result:
                response_data[region] = result[region]
            else:
                # Fallback stats if region not found
                response_data[region] = {
                    "avg_latency": 0.0,
                    "p95_latency": 0.0,
                    "avg_uptime": 0.0,
                    "breaches": 0
                }
        
        # Return as a top-level 'regions' object
        return {"regions": response_data}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
