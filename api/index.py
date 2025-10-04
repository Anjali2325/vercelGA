from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import json
import os
from typing import List, Dict, Any
import statistics

app = FastAPI()

# Enable CORS for all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST"],
    allow_headers=["*"],
)

class AnalysisRequest(BaseModel):
    regions: List[str]
    threshold_ms: int

# Load the telemetry data
def load_telemetry_data():
    try:
        # For Vercel deployment, file should be in same directory
        with open('q-vercel-latency.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        # Alternative path for local development
        with open('api/q-vercel-latency.json', 'r') as f:
            return json.load(f)

@app.post("/api/index")
async def analyze_latency(request: AnalysisRequest):
    try:
        data = load_telemetry_data()
        results = {}
        
        for region in request.regions:
            # Filter records for this region
            region_data = [item for item in data if item.get('region') == region]
            
            if not region_data:
                results[region] = {
                    "avg_latency": 0,
                    "p95_latency": 0,
                    "avg_uptime": 0,
                    "breaches": 0
                }
                continue
            
            # Extract latencies and uptimes
            latencies = [item['latency_ms'] for item in region_data]
            uptimes = [item['uptime'] for item in region_data]
            
            # Calculate metrics
            avg_latency = statistics.mean(latencies)
            p95_latency = statistics.quantiles(latencies, n=20)[-1]  # 95th percentile
            avg_uptime = statistics.mean(uptimes)
            breaches = sum(1 for latency in latencies if latency > request.threshold_ms)
            
            results[region] = {
                "avg_latency": round(avg_latency, 2),
                "p95_latency": round(p95_latency, 2),
                "avg_uptime": round(avg_uptime, 4),
                "breaches": breaches
            }
        
        return JSONResponse(content=results)
    
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Analysis failed: {str(e)}"}
        )

@app.get("/")
async def root():
    return {"message": "Latency Analysis API is running"}

# For Vercel serverless deployment
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
