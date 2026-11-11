
from io import BytesIO
from pathlib import Path

import pandas as pd
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware

from backend.validate_data import validate_csv
from backend.drift_detection import detect_data_drift


# Project directory
ROOT = Path(__file__).resolve().parents[1]

# Output CSV files
OUTPUT_DIR = ROOT / "outputs"

EFFECTS_PATH = OUTPUT_DIR / "customer_effects.csv"
OFFERS_PATH = OUTPUT_DIR / "optimized_offers.csv"


# Initialize FastAPI
app = FastAPI(
    title="EconoCausal API",
    description="REST API for causal machine learning and discount optimization.",
    version="1.0.0"
)


# Allow React frontend to communicate with FastAPI
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Helper function to load CSV files
def load_csv(file_path: Path, file_description: str):

    if not file_path.exists():
        raise HTTPException(
            status_code=404,
            detail=f"{file_description} not found. Generate the output file first."
        )

    try:
        return pd.read_csv(file_path)

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Unable to read {file_description}: {str(e)}"
        )


# Convert DataFrame into JSON-safe records
def dataframe_to_records(df):

    import json

    return json.loads(
        df.to_json(orient="records")
    )


# 1. Health check endpoint
@app.get("/api/health")
def health_check():

    return {
        "status": "healthy",
        "message": "EconoCausal API is running successfully!"
    }


# 2. Get customer-level causal effects
@app.get("/api/customer-effects")
def get_customer_effects():

    effects = load_csv(
        EFFECTS_PATH,
        "Customer effects file"
    )

    return dataframe_to_records(effects)


# 3. Get optimized customer offers
@app.get("/api/optimized-offers")
def get_optimized_offers():

    offers = load_csv(
        OFFERS_PATH,
        "Optimized offers file"
    )

    required_columns = [
        "customer_id",
        "previous_spend",
        "recommended_discount",
        "expected_incremental_benefit"
    ]

    missing = [
        col for col in required_columns
        if col not in offers.columns
    ]

    if missing:
        raise HTTPException(
            status_code=500,
            detail=f"Missing columns in optimized offers: {missing}"
        )

    return dataframe_to_records(offers)


# 4. Get discount allocation summary
@app.get("/api/allocation-summary")
def get_allocation_summary():

    offers = load_csv(
        OFFERS_PATH,
        "Optimized offers file"
    )

    required_columns = [
        "recommended_discount",
        "expected_incremental_benefit"
    ]

    missing = [
        col for col in required_columns
        if col not in offers.columns
    ]

    if missing:
        raise HTTPException(
            status_code=500,
            detail=f"Missing summary columns: {missing}"
        )

    # Convert columns to numeric values
    discounts = pd.to_numeric(
        offers["recommended_discount"],
        errors="coerce"
    ).fillna(0)

    benefits = pd.to_numeric(
        offers["expected_incremental_benefit"],
        errors="coerce"
    ).fillna(0)

    return {
        "total_customers": int(len(offers)),

        "total_discount_cost": round(
            float(discounts.sum()), 2
        ),

        "expected_incremental_benefit": round(
            float(benefits.sum()), 2
        )
    }


# 5. Upload and validate customer campaign CSV
@app.post("/api/upload-csv")
async def upload_csv(file: UploadFile = File(...)):

    try:
        # Read uploaded file
        file_content = await file.read()

        # Validate CSV
        validated_df = validate_csv(
            file_content,
            file.filename or ""
        )

        # Create upload directory
        upload_dir = ROOT / "data" / "uploads"
        upload_dir.mkdir(parents=True, exist_ok=True)

        # Save validated CSV using a fixed safe filename
        destination = upload_dir / "validated_customer_campaigns.csv"

        validated_df.to_csv(destination, index=False)

        return {
            "success": True,
            "message": "CSV uploaded and validated successfully!",
            "filename": file.filename,
            "total_records": int(len(validated_df)),
            "total_columns": int(len(validated_df.columns)),
            "columns": validated_df.columns.tolist(),
            "saved_as": "data/uploads/validated_customer_campaigns.csv"
        }

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc)
        )

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Unable to process uploaded CSV: {str(exc)}"
        )

    finally:
        await file.close()


# 6. Check customer data drift
@app.post("/api/check-drift")
async def check_drift(file: UploadFile = File(...)):

    try:
        # Read uploaded CSV
        contents = await file.read()

        current_df = pd.read_csv(
            BytesIO(contents)
        )

        # Load original cleaned training dataset
        reference_path = (
            ROOT / "data" / "customer_campaigns.csv"
        )

        if not reference_path.exists():
            raise HTTPException(
                status_code=500,
                detail="Original training dataset not found"
            )

        reference_df = pd.read_csv(reference_path)

        # Detect drift
        result = detect_data_drift(
            reference_df,
            current_df
        )

        return {
            "success": True,
            "message": "Drift detection completed",
            "result": result
        }

    except HTTPException:
        raise

    except (ValueError, KeyError) as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc)
        )

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Drift detection failed: {str(exc)}"
        )

    finally:
        await file.close()
