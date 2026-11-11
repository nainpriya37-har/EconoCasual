
import numpy as np
import pandas as pd


FEATURES = [
    "age",
    "previous_spend",
    "loyalty_score",
    "past_purchases"
]


def calculate_psi(reference, current, bins=10):
    """
    Calculate Population Stability Index (PSI)
    between reference and current distributions.
    """

    reference = pd.to_numeric(
        reference, errors="coerce"
    ).dropna()

    current = pd.to_numeric(
        current, errors="coerce"
    ).dropna()

    if reference.empty or current.empty:
        raise ValueError("Both datasets need valid numeric values.")

    # Create bins using the reference dataset
    quantiles = np.linspace(0, 1, bins + 1)

    edges = np.unique(
        reference.quantile(quantiles).to_numpy()
    )

    # Handle constant reference distributions
    if len(edges) == 1:
        edges = np.array([
            -np.inf, edges[0], np.inf
        ])
    else:
        edges[0] = -np.inf
        edges[-1] = np.inf

    # Calculate percentages in each bin
    reference_bins = pd.cut(
        reference, bins=edges, right=False
    )

    current_bins = pd.cut(
        current, bins=edges, right=False
    )

    reference_pct = (
        reference_bins.value_counts(sort=False)
        / len(reference)
    )

    current_pct = (
        current_bins.value_counts(sort=False)
        / len(current)
    )

    # Avoid division by zero
    epsilon = 0.0001

    reference_pct = np.clip(
        reference_pct.to_numpy(), epsilon, None
    )

    current_pct = np.clip(
        current_pct.to_numpy(), epsilon, None
    )

    psi = np.sum(
        (current_pct - reference_pct)
        * np.log(current_pct / reference_pct)
    )

    return float(psi)


def detect_data_drift(reference_df, current_df):

    results = {}

    for feature in FEATURES:

        if feature not in reference_df.columns:
            raise ValueError(
                f"{feature} missing in reference dataset"
            )

        if feature not in current_df.columns:
            raise ValueError(
                f"{feature} missing in uploaded dataset"
            )

        psi = calculate_psi(
            reference_df[feature],
            current_df[feature]
        )

        if psi < 0.10:
            level = "Low"
        elif psi <= 0.25:
            level = "Moderate"
        else:
            level = "High"

        results[feature] = {
            "psi": round(psi, 4),
            "drift_level": level
        }

    # Overall status is based on the highest feature PSI
    max_psi = max(
        result["psi"] for result in results.values()
    )

    if max_psi < 0.10:
        overall_status = "Low"
    elif max_psi <= 0.25:
        overall_status = "Moderate"
    else:
        overall_status = "High"

    return {
        "overall_status": overall_status,
        "features": results
    }
