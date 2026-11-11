
from pathlib import Path
import json
import numpy as np
import pandas as pd
from scipy.optimize import milp, LinearConstraint, Bounds

ROOT = Path(__file__).resolve().parents[1]

effects_path = ROOT / "outputs" / "customer_effects.csv"
config_path = ROOT / "config" / "optimization_config.json"

# Load customer effects
effects = pd.read_csv(effects_path)

# Generate customer IDs if they are missing
if "customer_id" not in effects.columns:
    effects.insert(
        0,
        "customer_id",
        [f"CUST_{i:04d}" for i in range(1, len(effects) + 1)]
    )

# Load optimization configuration
with open(config_path, encoding="utf-8") as f:
    config = json.load(f)

budget = float(config["budget"])
offers = [int(x) for x in config["discount_options"]]

# Validate required columns
required = [
    "customer_id",
    "previous_spend",
    "effect_10_vs_0",
    "effect_20_vs_0"
]

missing = [c for c in required if c not in effects.columns]

if missing:
    raise ValueError(
        f"Missing columns in customer_effects.csv: {missing}"
    )

# Check for duplicate customer IDs
if effects["customer_id"].duplicated().any():
    raise ValueError(
        "customer_effects.csv has duplicate customer IDs."
    )

# Check for invalid numeric values
if not np.isfinite(
    effects[
        ["previous_spend", "effect_10_vs_0", "effect_20_vs_0"]
    ].to_numpy(dtype=float)
).all():
    raise ValueError(
        "Effects file contains invalid numeric values."
    )

n = len(effects)
m = len(offers)

# One binary variable per customer-offer combination
# Variable index = customer_index * m + offer_index
benefits = np.zeros((n, m))

for i, customer in effects.iterrows():
    for j, offer in enumerate(offers):

        if offer == 0:
            effect = 0.0

        elif offer == 10:
            effect = float(customer["effect_10_vs_0"])

        elif offer == 20:
            effect = float(customer["effect_20_vs_0"])

        else:
            raise ValueError(
                f"Unsupported offer: {offer}. "
                "Add its treatment effect before using it."
            )

        benefits[i, j] = (
            effect * float(customer["previous_spend"])
        )

# Maximize benefit = minimize negative benefit
objective = -benefits.flatten()

# Each customer can receive at most one offer
customer_constraints = np.zeros((n, n * m))

for i in range(n):
    customer_constraints[i, i*m:(i+1)*m] = 1

customer_constraint = LinearConstraint(
    customer_constraints,
    lb=np.zeros(n),
    ub=np.ones(n)
)

# Total discount cost cannot exceed the budget
costs = np.tile(
    np.array(offers, dtype=float),
    n
)

budget_constraint = LinearConstraint(
    costs.reshape(1, -1),
    lb=-np.inf,
    ub=budget
)

# Run optimization
result = milp(
    c=objective,
    integrality=np.ones(n * m),
    bounds=Bounds(
        np.zeros(n * m),
        np.ones(n * m)
    ),
    constraints=[
        customer_constraint,
        budget_constraint
    ]
)

if not result.success:
    raise RuntimeError(
        f"Optimization failed: {result.message}"
    )

# Extract optimized decisions
decisions = np.rint(result.x).reshape(n, m)

selected_indices = decisions.argmax(axis=1)

selected_offers = [
    offers[j] if decisions[i, j] > 0.5 else 0
    for i, j in enumerate(selected_indices)
]

# Create final allocation
allocation = effects[
    ["customer_id", "previous_spend"]
].copy()

allocation["recommended_discount"] = selected_offers

allocation["expected_incremental_benefit"] = [
    benefits[i, selected_indices[i]]
    if selected_offers[i] != 0 else 0.0
    for i in range(n)
]

# Save output
OUTPUT = ROOT / "outputs"
OUTPUT.mkdir(exist_ok=True)

allocation.to_csv(
    OUTPUT / "optimized_offers.csv",
    index=False
)

# Display results
print("\nOptimization completed!")
print("\nRecommended customer offers:")
print(allocation.head(10))

print(
    "\nTotal discount cost:",
    sum(selected_offers)
)

print(
    "Expected incremental benefit:",
    allocation["expected_incremental_benefit"].sum()
)
