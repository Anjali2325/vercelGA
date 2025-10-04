from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import json
from typing import List
import statistics

app = FastAPI()

# Enable CORS for POST requests from any origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST"],
    allow_headers=["*"],
)

class AnalysisRequest(BaseModel):
    regions: List[str]
    threshold_ms: int

# Telemetry data matching the expected structure
TELEMETRY_DATA = [
    {"region": "emea", "latency_ms": 120, "uptime": 0.998},
    {"region": "amer", "latency_ms": 95, "uptime": 0.995},
    {"region": "emea", "latency_ms": 210, "uptime": 0.997},
    {"region": "amer", "latency_ms": 88, "uptime": 0.999},
    {"region": "emea", "latency_ms": 165, "uptime": 0.996},
    {"region": "amer", "latency_ms": 192, "uptime": 0.994},
    {"region": "emea", "latency_ms": 145, "uptime": 0.998},
    {"region": "amer", "latency_ms": 78, "uptime": 0.997},
    {"region": "emea", "latency_ms": 130, "uptime": 0.995},
    {"region": "amer", "latency_ms": 105, "uptime": 0.996},
    {"region": "emea", "latency_ms": 155, "uptime": 0.998},
    {"region": "amer", "latency_ms": 82, "uptime": 0.997}
]

@app.post("/api/analyze")
async def analyze_latency(request: AnalysisRequest):
    try:
        results = {}
        
        for region in request.regions:
            # Filter records for this region
            region_data = [item for item in TELEMETRY_DATA if item.get('region') == region]
            
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
            
            # Calculate 95th percentile properly
            sorted_latencies = sorted(latencies)
            n = len(sorted_latencies)
            p95_index = int(0.95 * n)
            p95_latency = sorted_latencies[p95_index] if n > 0 else 0
            
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
    return {"message": "Latency Analysis API - Use POST /api/analyze with {\"regions\":[\"emea\",\"amer\"],\"threshold_ms\":185}"}

# Vercel requires this
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
