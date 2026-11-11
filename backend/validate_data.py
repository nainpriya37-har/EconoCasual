
from pathlib import Path
from io import BytesIO
import json

import numpy as np
import pandas as pd


# ==========================================
# PROJECT PATHS
# ==========================================

ROOT = Path(__file__).resolve().parents[1]

DATA = ROOT / "data" / "customer_campaigns.csv"
OUTPUT = ROOT / "outputs"

OUTPUT.mkdir(parents=True, exist_ok=True)


# ==========================================
# REQUIRED CSV COLUMNS
# ==========================================

REQUIRED_COLUMNS = [
    "customer_id",
    "age",
    "past_purchases",
    "loyalty_score",
    "previous_spend",
    "discount",
    "purchased",
    "revenue",
]

NUMERIC_COLUMNS = [
    "age",
    "past_purchases",
    "loyalty_score",
    "previous_spend",
    "discount",
    "purchased",
    "revenue",
]


# ==========================================
# PART 1: CSV UPLOAD VALIDATION
# ==========================================

def validate_csv(file_content: bytes, filename: str):
    """
    Validate an uploaded customer campaign CSV.

    Returns:
        Validated pandas DataFrame.

    Raises:
        ValueError with an understandable error message.
    """

    # 1. Check CSV file format
    if not filename or not filename.lower().endswith(".csv"):
        raise ValueError(
            "Invalid file format. Please upload a CSV file."
        )

    # 2. Check empty file
    if not file_content or not file_content.strip():
        raise ValueError(
            "The uploaded CSV file is empty."
        )

    # 3. Read CSV file
    try:
        df = pd.read_csv(
            BytesIO(file_content),
            encoding="utf-8-sig"
        )

    except UnicodeDecodeError:
        raise ValueError(
            "Unable to read CSV. Please use UTF-8 encoding."
        )

    except Exception as exc:
        raise ValueError(
            f"Invalid CSV file. Unable to parse it: {exc}"
        )

    # 4. Check empty dataset
    if df.empty:
        raise ValueError(
            "The CSV contains no customer records."
        )

    # Remove spaces from column names
    df.columns = df.columns.astype(str).str.strip()

    # 5. Check required columns
    missing_columns = [
        column
        for column in REQUIRED_COLUMNS
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing required columns: {missing_columns}"
        )

    # 6. Check missing values
    missing_counts = (
        df[REQUIRED_COLUMNS]
        .isnull()
        .sum()
    )

    missing_counts = missing_counts[
        missing_counts > 0
    ]

    if not missing_counts.empty:
        details = ", ".join(
            f"{column}: {count}"
            for column, count in missing_counts.items()
        )

        raise ValueError(
            f"Missing values found: {details}"
        )

    # 7. Check blank customer IDs
    df["customer_id"] = (
        df["customer_id"]
        .astype(str)
        .str.strip()
    )

    blank_ids = df["customer_id"].eq("")

    if blank_ids.any():
        raise ValueError(
            f"Found {int(blank_ids.sum())} blank customer IDs."
        )

    # 8. Check duplicate customer IDs
    duplicate_mask = (
        df["customer_id"]
        .duplicated(keep=False)
    )

    if duplicate_mask.any():
        duplicate_ids = (
            df.loc[duplicate_mask, "customer_id"]
            .drop_duplicates()
            .head(5)
            .tolist()
        )

        raise ValueError(
            f"Duplicate customer IDs found: {duplicate_ids}"
        )

    # 9. Check invalid numeric values
    for column in NUMERIC_COLUMNS:

        converted = pd.to_numeric(
            df[column],
            errors="coerce"
        )

        invalid_mask = (
            converted.isna()
            | ~np.isfinite(converted.fillna(0))
        )

        if invalid_mask.any():
            invalid_rows = (
                df.index[invalid_mask] + 2
            ).tolist()[:5]

            raise ValueError(
                f"Invalid numeric values in '{column}'. "
                f"Check CSV row(s): {invalid_rows}."
            )

        df[column] = converted

    # 10. Validate purchased column
    if not df["purchased"].isin([0, 1]).all():
        raise ValueError(
            "The purchased column must contain only 0 or 1."
        )

    return df


# ==========================================
# PART 2: ORIGINAL DATA VALIDATION REPORT
# ==========================================

def generate_validation_report():

    if not DATA.exists():
        raise FileNotFoundError(
            f"Dataset not found: {DATA}"
        )

    df = pd.read_csv(DATA)

    # Check required columns
    missing_columns = [
        column
        for column in REQUIRED_COLUMNS
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing columns: {missing_columns}"
        )

    # Missing value report
    missing = df.isnull().sum().to_dict()

    # Treatment distribution
    treatment_counts = (
        df["discount"]
        .value_counts(dropna=False)
        .sort_index()
    )

    # Detect numeric outliers using IQR
    numeric = df.select_dtypes(
        include=np.number
    )

    outlier_counts = {}

    for column in numeric.columns:

        q1 = numeric[column].quantile(0.25)
        q3 = numeric[column].quantile(0.75)

        iqr = q3 - q1

        lower = q1 - 1.5 * iqr
        upper = q3 + 1.5 * iqr

        outlier_counts[column] = int(
            (
                (numeric[column] < lower)
                | (numeric[column] > upper)
            ).sum()
        )

    # Build report
    report = {
        "row_count": int(len(df)),

        "missing_values": {
            key: int(value)
            for key, value in missing.items()
        },

        "treatment_distribution": {
            str(key): int(value)
            for key, value in treatment_counts.items()
        },

        "outlier_counts": outlier_counts
    }

    # Save JSON report
    report_path = OUTPUT / "data_validation.json"

    with open(
        report_path,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            report,
            file,
            indent=4
        )

    print("Data validation completed!")

    print(
        json.dumps(
            report,
            indent=4
        )
    )

    print(f"\nReport saved at: {report_path}")


# ==========================================
# RUN REPORT WHEN EXECUTED DIRECTLY
# ==========================================

if __name__ == "__main__":
    generate_validation_report()
