# EconoCausal — Week 1 EDA Report

## Dataset overview

- Customers: 2000
- Columns: 8
- Duplicate customer IDs: 0
- Remaining missing cells: 0
- Overall observed purchase rate: 79.25%

## Discount distribution

discount
0     406
10    705
20    889

## Observed purchase rate by discount

 discount  purchase_rate  customers
        0       0.827586        406
       10       0.773050        705
       20       0.791901        889

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
