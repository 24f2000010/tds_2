from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import json
import numpy as np
from pathlib import Path

# Initialize the FastAPI app
app = FastAPI()

# CORS Configuration (no changes needed here)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["POST", "GET", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# --- THIS IS THE MODIFIED SECTION ---
# 1. Point to the new .json file
data_path = Path(__file__).parent / "telemetry.json"

# 2. Open the file and load the entire JSON array in one go
with open(data_path, "r") as f:
    telemetry_data = json.load(f)
# ------------------------------------

# Pydantic Model (no changes needed here)
class TelemetryRequest(BaseModel):
    regions: list[str]
    threshold_ms: int

# API Endpoint (no changes needed here)
@app.post("/api")
def process_telemetry(request: TelemetryRequest):
    results = {}
    for region in request.regions:
        region_data = [d for d in telemetry_data if d.get("region") == region]
        if not region_data:
            continue
        latencies = [d["latency_ms"] for d in region_data]
        uptimes = [d["uptime_pct"] for d in region_data]
        avg_latency = np.mean(latencies)
        p95_latency = np.percentile(latencies, 95)
        avg_uptime = np.mean(uptimes)
        breaches = np.sum(np.array(latencies) > request.threshold_ms)
        results[region] = {
            "avg_latency": round(avg_latency, 2),
            "p95_latency": round(p95_latency, 2),
            "avg_uptime": round(avg_uptime, 2),
            "breaches": int(breaches)
        }
    return {"regions": results}