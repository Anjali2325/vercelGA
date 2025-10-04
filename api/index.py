from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd
import numpy as np
import os

# Load telemetry bundle once on cold start
TELEMETRY_PATH = os.path.join(os.path.dirname(__file__), "..", "telemetry.csv")
df = pd.read_csv(TELEMETRY_PATH)  
# Expected columns: region, latency_ms, uptime (1 or 0)

app = FastAPI()

# Enable CORS for all origins and POST only
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
