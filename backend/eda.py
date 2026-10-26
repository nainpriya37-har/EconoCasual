
from pathlib import Path

import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data" / "customer_campaigns.csv"
OUTPUT_DIR = ROOT / "outputs"
REPORT_DIR = ROOT / "report"

OUTPUT_DIR.mkdir(exist_ok=True)
REPORT_DIR.mkdir(exist_ok=True)

df = pd.read_csv(DATA_PATH)
sns.set_theme(style="whitegrid")

# 1. Summary statistics
summary = df.describe(include="all").transpose()
summary.to_csv(OUTPUT_DIR / "eda_summary.csv")

# 2. Discount distribution
plt.figure(figsize=(7, 5))
sns.countplot(data=df, x="discount")
plt.title("Customers by Discount Level")
plt.xlabel("Discount ($)")
plt.ylabel("Number of Customers")
plt.tight_layout()
plt.savefig(OUTPUT_DIR / "discount_distribution.png", dpi=150)
plt.close()

# 3. Observed purchase rate by discount
purchase_rates = (
    df.groupby("discount")["purchased"]
    .agg(["mean", "count"])
    .reset_index()
)
purchase_rates.columns = ["discount", "purchase_rate", "customers"]
purchase_rates.to_csv(
    OUTPUT_DIR / "purchase_rate_by_discount.csv",
    index=False,
)

plt.figure(figsize=(7, 5))
sns.barplot(
    data=purchase_rates,
    x="discount",
    y="purchase_rate",
)
plt.title("Observed Purchase Rate by Discount")
plt.xlabel("Discount ($)")
plt.ylabel("Purchase Rate")
plt.ylim(0, 1)
plt.tight_layout()
plt.savefig(OUTPUT_DIR / "purchase_rate_by_discount.png", dpi=150)
plt.close()

# 4. Correlation heatmap
numeric_df = df.select_dtypes(include="number")

plt.figure(figsize=(9, 7))
sns.heatmap(
    numeric_df.corr(),
    annot=True,
    fmt=".2f",
    cmap="coolwarm",
    center=0,
)
plt.title("Numeric Feature Correlations")
plt.tight_layout()
plt.savefig(OUTPUT_DIR / "correlation_heatmap.png", dpi=150)
plt.close()

# 5. Missing-value report
missing = df.isna().sum().rename("missing_count")
missing.to_csv(OUTPUT_DIR / "missing_values.csv")

# 6. Generate the written report
total_customers = len(df)
overall_purchase_rate = df["purchased"].mean()
discount_counts = df["discount"].value_counts().sort_index()

report = f"""# EconoCausal — Week 1 EDA Report

## Dataset overview

- Customers: {total_customers}
- Columns: {len(df.columns)}
- Duplicate customer IDs: {df["customer_id"].duplicated().sum()}
- Remaining missing cells: {df.isna().sum().sum()}
- Overall observed purchase rate: {overall_purchase_rate:.2%}

## Discount distribution

{discount_counts.to_string()}

## Observed purchase rate by discount

{purchase_rates.to_string(index=False)}

## Generated figures

- `outputs/discount_distribution.png`
- `outputs/purchase_rate_by_discount.png`
- `outputs/correlation_heatmap.png`

## Initial observations

The dataset is simulated for educational use. Differences in
purchase rates across discount groups are descriptive associations
and should not be interpreted as causal effects.

The discount assignment process depends on customer
characteristics. These characteristics may act as confounders
when estimating the effect of discounts on purchasing.

## Limitations

- Results are based on synthetic data.
- Observed group differences are not causal estimates.
- Causal conclusions require assumptions and appropriate
  validation.
"""

report_path = REPORT_DIR / "week1_eda_report.md"
report_path.write_text(report, encoding="utf-8")

print("EDA completed.")
print(f"Report: {report_path}")
print(f"Charts and tables: {OUTPUT_DIR}")
print("\nPurchase rate by discount:")
print(purchase_rates.to_string(index=False))
