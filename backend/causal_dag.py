
from pathlib import Path

import pandas as pd
from dowhy import CausalModel

# Project paths
ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data" / "customer_campaigns.csv"
OUTPUT_DIR = ROOT / "outputs"
REPORT_DIR = ROOT / "report"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
REPORT_DIR.mkdir(parents=True, exist_ok=True)

# Load dataset
if not DATA_PATH.exists():
    raise FileNotFoundError(
        f"Dataset not found: {DATA_PATH}\n"
        "Run backend/clean_data.py first."
    )

df = pd.read_csv(DATA_PATH)

# Define treatment, outcome, and confounders
treatment = "discount"
outcome = "purchased"

confounders = [
    "age",
    "past_purchases",
    "loyalty_score",
    "previous_spend",
]

# Validate required columns
required_columns = confounders + [treatment, outcome]
missing_columns = [
    col for col in required_columns if col not in df.columns
]

if missing_columns:
    raise ValueError(
        f"Missing required columns in dataset: {missing_columns}"
    )

# Define the causal DAG using DOT syntax
edges = []

for variable in confounders:
    edges.append(f"{variable} -> {treatment}")
    edges.append(f"{variable} -> {outcome}")

edges.append(f"{treatment} -> {outcome}")

graph_lines = ["digraph {"]
for edge in edges:
    graph_lines.append(f"    {edge};")
graph_lines.append("}")

graph = "\n".join(graph_lines)

# Construct the causal model
model = CausalModel(
    data=df,
    treatment=treatment,
    outcome=outcome,
    graph=graph,
)

# Identify the causal estimand
identified_estimand = model.identify_effect(
    proceed_when_unidentifiable=True
)

# Save DOT graph
dot_lines = [
    "digraph EconoCausal {",
    "    rankdir=TB;",
]

for node in confounders + [treatment, outcome]:
    dot_lines.append(f'    "{node}";')

for edge in edges:
    source, target = [
        part.strip() for part in edge.split("->")
    ]
    dot_lines.append(f'    "{source}" -> "{target}";')

dot_lines.append("}")

dot_path = OUTPUT_DIR / "causal_dag.dot"
dot_path.write_text("\n".join(dot_lines), encoding="utf-8")

# Save report
documentation = f"""# EconoCausal Causal DAG

## Treatment
`{treatment}`

## Outcome
`{outcome}`

## Assumed confounders
{chr(10).join(f"- `{c}`" for c in confounders)}

## Directed edges
{chr(10).join(f"- {edge}" for edge in edges)}

## Model setup
DoWhy constructed the causal model and ran the
effect-identification step.

## Important limitations
This graph represents an assumed causal structure.
It does not estimate the treatment effect or prove
that all confounders have been observed.

The graph is a starting hypothesis for simulated data.
Real observational data requires domain knowledge
and further validation.
"""

report_path = REPORT_DIR / "causal_dag_report.md"
report_path.write_text(documentation, encoding="utf-8")

# Display results
print("Causal model created successfully!")
print(f"Treatment: {treatment}")
print(f"Outcome: {outcome}")
print(f"Confounders: {confounders}")
print(f"DAG saved to: {dot_path}")
print(f"Report saved to: {report_path}")

print("\nIdentified estimand:")
print(identified_estimand)
