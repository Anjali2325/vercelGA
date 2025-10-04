from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd
import numpy as np

# Sample telemetry inline (replace with real data if needed)
telemetry_data = [
    {"region": "emea", "latency_ms": 150, "uptime": 1},
    {"region": "emea", "latency_ms": 200, "uptime": 1},
    {"region": "emea", "latency_ms": 170, "uptime": 1},
    {"region": "amer", "latency_ms": 130, "uptime": 1},
    {"region": "amer", "latency_ms": 190, "uptime": 0},
    {"region": "amer", "latency_ms": 140, "uptime": 1},
]

df = pd.DataFrame(telemetry_data)

app = FastAPI()

# Enable CORS
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

        results[region] = {
            "avg_latency": round(float(latencies.mean()), 2),
            "p95_latency": round(float(np.percentile(latencies, 95)), 2),
            "avg_uptime": round(float(uptime.mean()), 4),
            "breaches": int((latencies > query.threshold_ms).sum()),
        }

    return results

# 👇 IMPORTANT: Vercel adapter
from mangum import Mangum
handler = Mangum(app)
