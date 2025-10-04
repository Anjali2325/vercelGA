from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd
import numpy as np

# --- Inline telemetry sample ---
# Replace with your real telemetry rows
telemetry_data = [
    {"region": "emea", "latency_ms": 150, "uptime": 1},
    {"region": "emea", "latency_ms": 200, "uptime": 1},
    {"region": "emea", "latency_ms": 170, "uptime": 1},
    {"region": "amer", "latency_ms": 130, "uptime": 1},
    {"region": "amer", "latency_ms": 190, "uptime": 0},
    {"region": "amer", "latency_ms": 140, "uptime": 1},
]

df = pd.DataFrame(telemetry_data)

# --- FastAPI App ---
app = FastAPI()

# Enable CORS (allow all origins, POST only)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST"],
    allow_headers=["*"],
)

class Query(BaseModel):
    regions: list[str]
    threshold_ms: int

@app.post("/")
async def metrics(query: Query):
    results = {}

    for region in query.regions:
        region_df = df[df["region"] == region]
        if region_df.empty:
            continue

        latencies = region_df["latency_ms"]
        uptime = region_df["uptime"]

        avg_latency = float(latencies.mean())
        p95_latency = float(np.percentile(latencies, 95))
        avg_uptime = float(uptime.mean())
        breaches = int((latencies > query.threshold_ms).sum())

        results[region] = {
            "avg_latency": round(avg_latency, 2),
            "p95_latency": round(p95_latency, 2),
            "avg_uptime": round(avg_uptime, 4),
            "breaches": breaches,
        }

    return results
