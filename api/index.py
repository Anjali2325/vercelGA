import json
import numpy as np
import pandas as pd
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

# Load telemetry data once at startup
with open("q-vercel-latency.json", "r") as f:
    telemetry = json.load(f)

df = pd.DataFrame(telemetry)

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)



@app.post("/")
async def check_latency(request: Request):
    body = await request.json()
    regions = body.get("regions", [])
    threshold = body.get("threshold_ms", 180)

    results = {}

    for region in regions:
        region_df = df[df["region"] == region]

        if region_df.empty:
            continue

        avg_latency = float(region_df["latency_ms"].mean())
        p95_latency = float(np.percentile(region_df["latency_ms"], 95))
        avg_uptime = float(region_df["uptime"].mean())
        breaches = int((region_df["latency_ms"] > threshold).sum())

        results[region] = {
            "avg_latency": round(avg_latency, 2),
            "p95_latency": round(p95_latency, 2),
            "avg_uptime": round(avg_uptime, 2),
            "breaches": breaches
        }

    return results
