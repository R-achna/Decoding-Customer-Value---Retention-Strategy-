import streamlit as st
from utils import load_data

st.set_page_config(page_title="Methodology", page_icon="📋", layout="wide")

df = load_data()

st.title("📋 Methodology & Data Limitations")
st.caption("Every engineered metric traced back to its logic, plus honest disclosure of what the data can't tell us.")

st.subheader("Feature Dictionary")

st.markdown("""
| Column | Formula / Logic | Business Question Answered |
|---|---|---|
| `Estimated_Lifetime_Spend` | Order value × (Previous Purchases + 1) | How much revenue has this customer likely generated? *(Assumes observed order is representative of typical order size — a stated assumption, not a fact.)* |
| `Value_Tier` | Quartile bucket of Estimated Lifetime Spend | Which customers deserve priority treatment? |
| `Loyalty_Score_A_Behavioral` | Percentile rank of Previous Purchases (tie-broken by spend for the 77 customers censored at the max value of 50) | How much purchase history has this customer built? *(Built on a single validated field — Frequency of Purchases and Subscription Status were tested and excluded after showing no significant relationship, p > 0.1)* |
| `Engagement_Depth_Tier` | Quartile bucket of Loyalty Score A | New / Developing / Established / Veteran — actionable tenure labels |
| `Loyalty_Score_B_Value_Satisfaction` | 50% Estimated Lifetime Spend percentile + 50% Review Rating percentile | Is this customer's relationship both profitable and sustainable? |
| `Customer_Segment` | Four-quadrant label from Loyalty A × Loyalty B (75th percentile thresholds) | Who is genuinely loyal vs. discount-only vs. new vs. low-priority? |
| `Promo_Dependency_Score` | Percentile rank of discount usage, computed *within gender* | How reliant is this customer on discounts, corrected for a structural data artifact (see below) |
| `Region` | US state rolled up to 4 census regions | Statistically stable geographic grouping (most states have only 60-90 customers) |
| `Tenure_Censored_Flag` | 1 if Previous Purchases = 50 (the dataset max) | Flags customers whose true tenure may be understated |
| `Frequency_Inconsistency_Flag` | 1 if stated purchase frequency is implausible given purchase count | Flags data quality issues rather than silently trusting inconsistent fields |
""")

st.markdown("---")

st.subheader("⚠️ Data Limitations (Read Before Trusting Any Number Above)")

st.markdown("""
**1. Discount usage is confounded with Gender and Subscription Status, not a clean behavioral signal.**
In this dataset, 0% of Female customers show `Discount Applied = Yes`, while ~63% of Male customers do —
and 100% of subscribers show discount usage. This is a structural artifact of how the data was generated,
not evidence of real customer choice. `Promo_Dependency_Score` is therefore ranked *within gender* to avoid
letting this artifact masquerade as a business insight — but any promo-related finding should be read with
this caveat in mind.

**2. Frequency of Purchases carries no validated relationship to actual purchase history.**
A multivariate regression (controlling for Age, Gender, and Category) found stated purchase frequency
("Weekly," "Annually," etc.) adds no statistically significant explanatory power for `Previous Purchases`
(p = 0.118). ~10% of customer profiles show a frequency label that's implausible given their purchase count
(e.g., "Annually" combined with 30+ previous purchases). This field is kept in the dataset for descriptive
use but was deliberately excluded from every loyalty/value score.

**3. Previous Purchases is censored at 50.**
About 2% of customers sit exactly at this ceiling — their true purchase history may be higher than recorded.
Ties within this group are broken using estimated spend as a secondary sort, but the underlying censoring
itself can't be corrected without more data.

**4. This is a single-snapshot dataset — there are no timestamps.**
Every "loyalty" and "value" measure here is a current-state behavioral proxy, not an observed pattern over
time. Claims about future retention should be understood as propensity estimates, not predictions validated
against actual outcomes.

**5. Missing Review Ratings (37 customers, <1%) were imputed using the category median**,
after confirming the missingness pattern was not concentrated in any one category (i.e., appears random,
not structural).
""")

st.markdown("---")
st.caption(f"Dataset: {len(df):,} customers · synthetic D2C fashion brand data")
