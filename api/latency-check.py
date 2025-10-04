from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import numpy as np
import pandas as pd
import json

app = FastAPI()

# ✅ Enable CORS for POST from any origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST"],
    allow_headers=["*"],
)

# ✅ Load telemetry data once (adjust path if needed)
telemetry = pd.read_csv("telemetry.csv")

@app.post("/api/latency-check")
async def latency_check(request: Request):
    body = await request.json()
    regions = body.get("regions", [])
    threshold = body.get("threshold_ms", 180)

    results = {}
    for region in regions:
        region_data = telemetry[telemetry["region"] == region]
        latencies = region_data["latency_ms"]
        uptimes = region_data["uptime_pct"]

        breaches = (latencies > threshold).sum()
        results[region] = {
            "avg_latency": round(latencies.mean(), 2),
            "p95_latency": round(np.percentile(latencies, 95), 2),
            "avg_uptime": round(uptimes.mean(), 2),
            "breaches": int(breaches)
        }

    return results
