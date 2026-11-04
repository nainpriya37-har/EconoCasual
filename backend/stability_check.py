
from pathlib import Path
import json
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor

ROOT = Path(__file__).resolve().parents[1]
df = pd.read_csv(ROOT / "data" / "customer_campaigns.csv")

features = [
    "age", "past_purchases",
    "loyalty_score", "previous_spend"
]

required = features + ["discount", "purchased"]
df = df[required].dropna()

# Compare the estimated effect across repeated random splits.
estimates = []

for seed in range(5):
    rng = np.random.default_rng(seed)
    sample = df.sample(
        frac=0.8, random_state=seed
    )

    treated = sample[sample["discount"] > 0]
    control = sample[sample["discount"] == 0]

    if len(treated) < 10 or len(control) < 10:
        continue

    model_treated = RandomForestRegressor(
        n_estimators=100, random_state=seed
    )
    model_control = RandomForestRegressor(
        n_estimators=100, random_state=seed
    )

    model_treated.fit(
        treated[features], treated["purchased"]
    )
    model_control.fit(
        control[features], control["purchased"]
    )

    difference = (
        model_treated.predict(sample[features]).mean()
        - model_control.predict(sample[features]).mean()
    )

    estimates.append(float(difference))

if not estimates:
    raise ValueError(
        "Not enough treated/control customers for stability testing."
    )

report = {
    "number_of_runs": len(estimates),
    "estimates": estimates,
    "mean_estimate": float(np.mean(estimates)),
    "standard_deviation": float(np.std(estimates)),
    "min_estimate": float(np.min(estimates)),
    "max_estimate": float(np.max(estimates)),
    "interpretation": (
        "Compare estimates across runs. Large variation "
        "may indicate instability."
    )
}

OUTPUT = ROOT / "outputs"
OUTPUT.mkdir(exist_ok=True)

with open(OUTPUT / "stability_report.json", "w") as f:
    json.dump(report, f, indent=4)

print(json.dumps(report, indent=4))
