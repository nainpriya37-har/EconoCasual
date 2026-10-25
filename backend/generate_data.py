
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
DATA_DIR.mkdir(exist_ok=True)

rng = np.random.default_rng(42)
n = 2000

# Customer characteristics
age = rng.integers(18, 66, size=n)
past_purchases = rng.poisson(4, size=n)
loyalty_score = rng.uniform(0, 1, size=n)
previous_spend = np.maximum(
    10, rng.normal(150, 60, size=n)
).round(2)

# Simulated discount assignment:
# Customers with fewer past purchases tend to receive larger discounts.
assignment_score = (
    0.8
    - 0.12 * past_purchases
    - 0.5 * loyalty_score
    + rng.normal(0, 1, size=n)
)

discount = np.where(
    assignment_score > 0.2,
    20,
    np.where(assignment_score > -0.8, 10, 0),
)

# Simulated purchase probability.
# This is a teaching example, not a real-world causal estimate.
base_logit = (
    -1.0
    + 0.035 * (age - 35)
    + 0.20 * past_purchases
    + 1.0 * loyalty_score
    + 0.003 * previous_spend
)

# Assume discounts have a positive average effect in this
# simulated world. The real effect is unknown in real data.
discount_effect = np.where(discount == 10, 0.35, 0.60)

probability = 1 / (
    1 + np.exp(-(base_logit + discount_effect))
)

purchased = rng.binomial(1, probability)

# Revenue is observed only when a purchase occurs.
order_value = np.where(
    purchased == 1,
    np.maximum(
        5,
        previous_spend * rng.uniform(0.5, 1.5, size=n)
        - discount,
    ).round(2),
    0.0,
)

df = pd.DataFrame({
    "customer_id": [
        f"C{i:04d}" for i in range(1, n + 1)
    ],
    "age": age,
    "past_purchases": past_purchases,
    "loyalty_score": loyalty_score.round(3),
    "previous_spend": previous_spend,
    "discount": discount,
    "purchased": purchased,
    "revenue": order_value,
})

# Introduce a small number of missing values so the
# cleaning step can demonstrate missing-data handling.
df.loc[rng.choice(n, 20, replace=False), "loyalty_score"] = np.nan

raw_path = DATA_DIR / "customer_campaigns_raw.csv"
df.to_csv(raw_path, index=False)

print(f"Generated {len(df)} customer records.")
print(f"Saved raw data to: {raw_path}")
print("\nDiscount distribution:")
print(df["discount"].value_counts().sort_index())
print("\nPurchase rate:")
print(df["purchased"].mean().round(3))
