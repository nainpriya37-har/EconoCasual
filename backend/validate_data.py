
from pathlib import Path
import json
import pandas as pd
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "customer_campaigns.csv"
OUTPUT = ROOT / "outputs"

OUTPUT.mkdir(exist_ok=True)

df = pd.read_csv(DATA)

required = [
    "customer_id", "age", "past_purchases",
    "loyalty_score", "previous_spend",
    "discount", "purchased"
]

missing_columns = [c for c in required if c not in df.columns]

if missing_columns:
    raise ValueError(f"Missing columns: {missing_columns}")

missing = df.isnull().sum().to_dict()

treatment_counts = (
    df["discount"].value_counts(dropna=False).sort_index()
)

numeric = df.select_dtypes(include=np.number)
outlier_counts = {}

for column in numeric.columns:
    q1 = numeric[column].quantile(0.25)
    q3 = numeric[column].quantile(0.75)
    iqr = q3 - q1

    lower = q1 - 1.5 * iqr
    upper = q3 + 1.5 * iqr

    outlier_counts[column] = int(
        ((numeric[column] < lower) |
         (numeric[column] > upper)).sum()
    )

report = {
    "row_count": int(len(df)),
    "missing_values": {
        k: int(v) for k, v in missing.items()
    },
    "treatment_distribution": {
        str(k): int(v)
        for k, v in treatment_counts.items()
    },
    "outlier_counts": outlier_counts
}

with open(OUTPUT / "data_validation.json", "w") as f:
    json.dump(report, f, indent=4)

print("Data validation completed!")
print(json.dumps(report, indent=4))
