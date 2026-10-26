
from pathlib import Path

import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / "outputs"

app = FastAPI(title="EconoCausal API")

# Allow your local React development server to call this API.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def home():
    return {"message": "EconoCausal API is running"}


@app.get("/api/customer-effects")
def customer_effects():
    path = OUTPUT_DIR / "customer_effects.csv"

    if not path.exists():
        raise HTTPException(
            status_code=404,
            detail="Run the causal training script first.",
        )

    df = pd.read_csv(path)
    return df.to_dict(orient="records")


@app.get("/api/metrics")
def metrics():
    path = OUTPUT_DIR / "causal_metrics.json"

    if not path.exists():
        raise HTTPException(
            status_code=404,
            detail="Evaluation metrics are not available yet.",
        )

    import json

    with open(path, encoding="utf-8") as file:
        return json.load(file)


@app.get("/api/discount-options")
def discount_options():
    path = OUTPUT_DIR / "discount_options.json"

    if not path.exists():
        raise HTTPException(
            status_code=404,
            detail="Discount options are not available yet.",
        )

    import json

    with open(path, encoding="utf-8") as file:
        return json.load(file)
