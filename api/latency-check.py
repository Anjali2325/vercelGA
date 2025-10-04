from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import numpy as np
from pydantic import BaseModel
from typing import List
import json

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST"],
    allow_headers=["*"],
)

class Payload(BaseModel):
    regions: List[str]
    threshold_ms: int

# Load telemetry bundle (pretend it's downloaded and bundled with deployment)
with open("telemetry.json") as f:
    telemetry = json.load(f)

@app.post("/api/telemetry")
async def telemetry_endpoint(payload: Payload):
    results = {}
    for region in payload.regions:
        data = telemetry.get(region, [])
        if not data:
            continue
        latencies = [d["latency_ms"] for d in data]
        uptimes = [d["uptime"] for d in data]

        breaches = sum(1 for l in latencies if l > payload.threshold_ms)
        avg_latency = float(np.mean(latencies))
        p95_latency = float(np.percentile(latencies, 95))
        avg_uptime = float(np.mean(uptimes))

        results[region] = {
            "avg_latency": avg_latency,
            "p95_latency": p95_latency,
            "avg_uptime": avg_uptime,
            "breaches": breaches,
        }
    return results
