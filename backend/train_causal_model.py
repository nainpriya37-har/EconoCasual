
from pathlib import Path
import json

import joblib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor

from econml.dml import CausalForestDML
from sklift.metrics import uplift_curve, qini_curve, qini_auc_score


# --------------------------------------------------
# 1. Paths and folders
# --------------------------------------------------

ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data" / "customer_campaigns.csv"
OUTPUT_DIR = ROOT / "outputs"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# --------------------------------------------------
# 2. Load and validate the data
# --------------------------------------------------

df = pd.read_csv(DATA_PATH)

treatment = "discount"
outcome = "purchased"

confounders = [
    "age",
    "past_purchases",
    "loyalty_score",
    "previous_spend",
]

required = confounders + [treatment, outcome]
missing = [col for col in required if col not in df.columns]

if missing:
    raise ValueError(f"Missing required columns: {missing}")

df = df[required].dropna().copy()

if df[outcome].nunique() != 2:
    raise ValueError("'purchased' must contain two classes, such as 0 and 1.")

treatment_levels = sorted(df[treatment].unique().tolist())

if len(treatment_levels) < 2:
    raise ValueError("At least two discount options are required.")

if len(treatment_levels) > 10:
    raise ValueError(
        "More than 10 unique discount values found. "
        "Check whether discount should be treated as continuous."
    )

print("Dataset shape:", df.shape)
print("Discount options:", treatment_levels)
print("Purchase rate:", round(df[outcome].mean(), 4))

# --------------------------------------------------
# 3. Prepare features, treatment and outcome
# --------------------------------------------------

X = df[confounders]
T = df[treatment]
y = df[outcome].astype(int)

# Keep a separate test set for uplift/Qini evaluation.
train_idx, test_idx = train_test_split(
    np.arange(len(df)),
    test_size=0.25,
    random_state=42,
)

X_train = X.iloc[train_idx]
T_train = T.iloc[train_idx]
y_train = y.iloc[train_idx]

X_test = X.iloc[test_idx]
T_test = T.iloc[test_idx]
y_test = y.iloc[test_idx]

# --------------------------------------------------
# 4. Train the causal forest
# --------------------------------------------------

model = CausalForestDML(
    model_y=RandomForestRegressor(
        n_estimators=100,
        min_samples_leaf=5,
        random_state=42,
        n_jobs=-1,
    ),
    model_t=RandomForestClassifier(
        n_estimators=100,
        min_samples_leaf=5,
        random_state=42,
        n_jobs=-1,
    ),
    discrete_treatment=True,
    n_estimators=200,
    min_samples_leaf=5,
    cv=3,
    random_state=42,
)

model.fit(y_train, T_train, X=X_train)

model_path = OUTPUT_DIR / "causal_forest_model.joblib"
joblib.dump(model, model_path)

print("Causal model trained and saved:", model_path)

# --------------------------------------------------
# 5. Estimate effects for each customer
# --------------------------------------------------

baseline = treatment_levels[0]
customer_effects = X.copy()

for level in treatment_levels[1:]:
    effect = model.effect(
        X,
        T0=baseline,
        T1=level,
    )
    customer_effects[f"effect_{level}_vs_{baseline}"] = effect

customer_effects[treatment] = T.values
customer_effects[outcome] = y.values

effects_path = OUTPUT_DIR / "customer_effects.csv"
customer_effects.to_csv(effects_path, index=False)

print("Customer effects saved:", effects_path)

# --------------------------------------------------
# 6. Evaluate the strongest discount vs baseline
# --------------------------------------------------

target = treatment_levels[-1]

# Evaluate only the baseline and target arms.
mask = T_test.isin([baseline, target])

T_eval = T_test.loc[mask]
y_eval = y_test.loc[mask]
X_eval = X_test.loc[mask]

if (
    len(X_eval) > 0
    and T_eval.nunique() == 2
    and y_eval.nunique() == 2
):
    uplift_scores = model.effect(
        X_eval,
        T0=baseline,
        T1=target,
    )

    # Qini/uplift metrics require a binary treatment indicator.
    treated = (T_eval == target).astype(int).to_numpy()
    outcomes = y_eval.to_numpy()

    # Uplift curve
    x_uplift, y_uplift = uplift_curve(
        outcomes, uplift_scores, treated
    )

    plt.figure(figsize=(8, 5))
    plt.plot(x_uplift, y_uplift, label="Causal forest")
    plt.xlabel("Number of customers targeted")
    plt.ylabel("Cumulative incremental responses")
    plt.title(f"Uplift: discount {target} vs {baseline}")
    plt.legend()
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "uplift_curve.png", dpi=150)
    plt.close()

    # Qini curve
    x_qini, y_qini = qini_curve(
        outcomes, uplift_scores, treated
    )

    plt.figure(figsize=(8, 5))
    plt.plot(x_qini, y_qini, label="Causal forest")
    plt.xlabel("Number of customers targeted")
    plt.ylabel("Cumulative incremental responses")
    plt.title(f"Qini: discount {target} vs {baseline}")
    plt.legend()
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "qini_curve.png", dpi=150)
    plt.close()

    qini_auc = qini_auc_score(
        outcomes, uplift_scores, treated
    )

    metrics = {
        "baseline_discount": float(baseline),
        "target_discount": float(target),
        "evaluation_customers": int(len(X_eval)),
        "qini_auc": float(qini_auc),
    }

    with open(
        OUTPUT_DIR / "causal_metrics.json",
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(metrics, file, indent=2)

    print("Qini AUC:", round(float(qini_auc), 4))
    print("Uplift and Qini charts saved.")

else:
    print(
        "Uplift/Qini evaluation skipped: the held-out data "
        "needs both treatment groups and both outcome classes."
    )

# --------------------------------------------------
# 7. Export discount options for the dashboard
# --------------------------------------------------

with open(
    OUTPUT_DIR / "discount_options.json",
    "w",
    encoding="utf-8",
) as file:
    json.dump(
        {"discount_options": [float(v) for v in treatment_levels]},
        file,
        indent=2,
    )

print("\nWeek 2 training process completed.")
