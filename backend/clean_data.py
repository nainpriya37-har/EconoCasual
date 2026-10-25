
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
OUTPUT_DIR = ROOT / "outputs"
OUTPUT_DIR.mkdir(exist_ok=True)

raw_path = DATA_DIR / "customer_campaigns_raw.csv"
clean_path = DATA_DIR / "customer_campaigns.csv"

df = pd.read_csv(raw_path)

required_columns = [
    "customer_id",
    "age",
    "past_purchases",
    "loyalty_score",
    "previous_spend",
    "discount",
    "purchased",
    "revenue",
]

missing_columns = set(required_columns) - set(df.columns)
if missing_columns:
    raise ValueError(f"Missing columns: {sorted(missing_columns)}")

df = df[required_columns].copy()

before = len(df)

# Remove duplicate customer IDs.
df = df.drop_duplicates(subset="customer_id")

# Validate key values.
df = df.dropna(subset=["customer_id", "discount", "purchased"])
df = df[df["age"].between(18, 100)]
df = df[df["discount"].isin([0, 10, 20])]
df = df[df["purchased"].isin([0, 1])]
df = df[df["revenue"] >= 0]

# Fill missing loyalty scores with the median.
df["loyalty_score"] = df["loyalty_score"].fillna(
    df["loyalty_score"].median()
)

# Validate missing values after cleaning.
if df[required_columns].isna().any().any():
    raise ValueError("Unexpected missing values remain.")

# Store validation summary.
summary = pd.DataFrame({
    "metric": [
        "rows_before_cleaning",
        "rows_after_cleaning",
        "rows_removed",
        "duplicate_customer_ids_after_cleaning",
        "remaining_missing_cells",
    ],
    "value": [
        before,
        len(df),
        before - len(df),
        int(df["customer_id"].duplicated().sum()),
        int(df.isna().sum().sum()),
    ],
})

summary.to_csv(OUTPUT_DIR / "data_quality_summary.csv", index=False)
df.to_csv(clean_path, index=False)

print(summary.to_string(index=False))
print(f"\nCleaned dataset saved to: {clean_path}")
