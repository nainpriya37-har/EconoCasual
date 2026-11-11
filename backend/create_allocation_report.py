
from pathlib import Path
import json
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "outputs"

allocation = pd.read_csv(
    OUTPUT / "optimized_offers.csv"
)

with open(
    ROOT / "config" / "optimization_config.json",
    encoding="utf-8"
) as f:
    config = json.load(f)

budget = float(config["budget"])

total_cost = float(
    allocation["recommended_discount"].sum()
)

total_benefit = float(
    allocation["expected_incremental_benefit"].sum()
)

summary = {
    "total_customers": int(len(allocation)),
    "customers_receiving_discount": int(
        (allocation["recommended_discount"] > 0).sum()
    ),
    "customers_receiving_no_discount": int(
        (allocation["recommended_discount"] == 0).sum()
    ),
    "campaign_budget": budget,
    "budget_used": total_cost,
    "remaining_budget": budget - total_cost,
    "budget_utilization_percent": (
        total_cost / budget * 100 if budget > 0 else 0
    ),
    "total_expected_incremental_benefit": total_benefit
}

allocation["offer_0"] = (
    allocation["recommended_discount"] == 0
).astype(int)

allocation["offer_10"] = (
    allocation["recommended_discount"] == 10
).astype(int)

allocation["offer_20"] = (
    allocation["recommended_discount"] == 20
).astype(int)

allocation.to_csv(
    OUTPUT / "allocation_matrix.csv",
    index=False
)

with open(
    OUTPUT / "allocation_summary.json",
    "w",
    encoding="utf-8"
) as f:
    json.dump(summary, f, indent=4)

print("Allocation report generated.")
print(json.dumps(summary, indent=4))
