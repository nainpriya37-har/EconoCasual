
from pathlib import Path
import json
import pandas as pd
from dowhy import CausalModel

# --------------------------------------------------
# 1. Load dataset
# --------------------------------------------------

ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data" / "customer_campaigns.csv"

OUTPUT = ROOT / "outputs"
OUTPUT.mkdir(parents=True, exist_ok=True)

df = pd.read_csv(DATA_PATH)

# --------------------------------------------------
# 2. Define columns and prepare data
# --------------------------------------------------

confounders = [
    "age",
    "past_purchases",
    "loyalty_score",
    "previous_spend"
]

required = ["discount", "purchased"] + confounders

missing = [col for col in required if col not in df.columns]

if missing:
    raise ValueError(f"Missing required columns: {missing}")

df = df[required].dropna().copy()

# Compare only customers receiving 0 or 10 discount
df = df[df["discount"].isin([0, 10])].copy()

if df.empty:
    raise ValueError("No customers found with discount 0 or 10.")

# Convert discount into binary treatment:
# 0 = no discount
# 1 = ₹10 discount
df["treatment"] = (df["discount"] == 10).astype(int)

if df["treatment"].nunique() < 2:
    raise ValueError(
        "Both discount groups (0 and 10) are required for this analysis."
    )

# Ensure outcome is numeric
df["purchased"] = pd.to_numeric(
    df["purchased"], errors="coerce"
)

df = df.dropna(subset=["purchased"])

# --------------------------------------------------
# 3. Create causal model
# --------------------------------------------------

model = CausalModel(
    data=df,
    treatment="treatment",
    outcome="purchased",
    common_causes=confounders
)

identified = model.identify_effect()

# --------------------------------------------------
# 4. Estimate causal effect
# --------------------------------------------------

estimate = model.estimate_effect(
    identified,
    method_name="backdoor.propensity_score_matching"
)

print("\nOriginal causal estimate:", estimate.value)

# --------------------------------------------------
# 5. Run refutation tests
# --------------------------------------------------

results = {
    "comparison": "₹10 discount vs ₹0 discount",
    "sample_size": int(len(df)),
    "control_customers": int((df["treatment"] == 0).sum()),
    "treated_customers": int((df["treatment"] == 1).sum()),
    "original_estimate": float(estimate.value),
    "refutations": {}
}

tests = {
    "placebo_treatment": "placebo_treatment_refuter",
    "random_common_cause": "add_random_common_cause"
}

for test_name, method_name in tests.items():

    try:
        result = model.refute_estimate(
            identified,
            estimate,
            method_name=method_name
        )

        results["refutations"][test_name] = str(result)

        print(f"\n{test_name}:")
        print(result)

    except Exception as error:

        results["refutations"][test_name] = {
            "error": str(error)
        }

        print(f"\n{test_name} could not run: {error}")

# --------------------------------------------------
# 6. Save results
# --------------------------------------------------

output_file = OUTPUT / "refutation_results.json"

with open(output_file, "w", encoding="utf-8") as file:
    json.dump(results, file, indent=4)

print("\nRefutation testing completed.")
print("Results saved to:", output_file)
