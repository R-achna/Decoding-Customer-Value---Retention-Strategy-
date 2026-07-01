import streamlit as st
import pandas as pd
import plotly.express as px
from utils import load_data, sidebar_filters, SEGMENT_ORDER, SEGMENT_COLORS, SEGMENT_ACTIONS

st.set_page_config(page_title="Promo Sunset Plan", page_icon="💰", layout="wide")

df = load_data()
filtered = sidebar_filters(df, key_prefix="promo")

st.title("💰 Promotional Sunset Plan")
st.caption("The specific recommendation: which segment to pull discounts from, why, and the estimated margin impact.")

# ============================================================================
# SEGMENT ACTION TABLE
# ============================================================================
st.subheader("Recommended Action by Segment")

seg_summary = (
    filtered.groupby('Customer_Segment', observed=True)
    .agg(customers=('Customer ID', 'count'),
         pct_using_discount=('Discount Applied_Flag', 'mean'),
         avg_promo_dependency=('Promo_Dependency_Score', 'mean'),
         avg_spend=('Estimated_Lifetime_Spend', 'mean'),
         total_spend=('Estimated_Lifetime_Spend', 'sum'))
    .reindex(SEGMENT_ORDER).reset_index()
)
seg_summary['pct_using_discount'] *= 100
seg_summary['Recommended Action'] = seg_summary['Customer_Segment'].map(SEGMENT_ACTIONS)

display_table = seg_summary[[
    'Customer_Segment', 'customers', 'pct_using_discount', 'avg_spend', 'Recommended Action'
]].rename(columns={
    'Customer_Segment': 'Segment', 'customers': 'Customers',
    'pct_using_discount': '% Using Discount', 'avg_spend': 'Avg. Lifetime Spend'
})
st.dataframe(
    display_table.style.format({'% Using Discount': '{:.1f}%', 'Avg. Lifetime Spend': '${:,.0f}'}),
    use_container_width=True, hide_index=True
)

st.markdown("""
**Headline recommendation:** Begin a phased discount reduction for the **"Habitual, Not Yet Valuable"**
segment — customers with a proven purchase habit but the highest discount reliance in the base.
Their existing purchase pattern suggests demand may hold even as the discount is reduced.

- **Trigger behavior:** 3+ previous purchases combined with above-median promo dependency score
- **Rollout:** phased — reduce discount depth by ~30% for a test cohort, monitor for 60-90 days
- **Metric to track:** repeat purchase rate and average order value within the test cohort,
  compared against a held-out control group that keeps the existing discount
- **Protect, don't touch:** "Core Loyal" (already low discount reliance — no action needed)
  and "Promising New" (discount may still be doing real acquisition/conversion work for
  newer customers — reducing here risks losing them before the relationship is established)
""")

st.markdown("---")

# ============================================================================
# WHAT-IF SIMULATOR
# ============================================================================
st.subheader("🧮 What-If Simulator: Discount Reduction Impact")

st.warning(
    "⚠️ **Illustrative only.** This dataset does not include margin, COGS, or true "
    "discount depth — only whether a discount was applied. The estimate below uses "
    "your own assumptions for discount depth and retained-demand rate, applied to "
    "the real spend figures in this dataset. Use it to reason about direction and "
    "scale, not as a precise financial forecast."
)

sim_col1, sim_col2, sim_col3 = st.columns(3)
with sim_col1:
    target_segment = st.selectbox("Target segment for discount reduction:", SEGMENT_ORDER, index=1)
with sim_col2:
    discount_depth = st.slider("Assumed avg. discount depth (%)", 5, 40, 15)
with sim_col3:
    demand_retention = st.slider("Assumed demand retained after removing discount (%)", 50, 100, 85)

seg_row = seg_summary[seg_summary['Customer_Segment'] == target_segment].iloc[0]
customers_affected = int(seg_row['customers'])
pct_currently_discounting = seg_row['pct_using_discount'] / 100
current_spend = seg_row['total_spend']

# Illustrative model:
# - Only the discounting sub-population's spend is exposed to margin recovery.
# - Margin recovered = discount depth saved on retained spend.
# - Revenue at risk = spend lost from the (1 - demand_retention) portion that churns.
discounting_spend = current_spend * pct_currently_discounting
retained_spend = discounting_spend * (demand_retention / 100)
lost_spend = discounting_spend - retained_spend
margin_recovered = retained_spend * (discount_depth / 100)
net_impact = margin_recovered - lost_spend

r1, r2, r3, r4 = st.columns(4)
r1.metric("Customers Affected", f"{customers_affected:,}")
r2.metric("Est. Margin Recovered", f"${margin_recovered:,.0f}")
r3.metric("Est. Revenue at Risk", f"-${lost_spend:,.0f}")
r4.metric("Net Estimated Impact", f"${net_impact:,.0f}", delta=f"{'Positive' if net_impact > 0 else 'Negative'}")

st.caption(
    f"Model: of the {customers_affected:,} customers in *{target_segment}*, "
    f"{pct_currently_discounting:.0%} currently use a discount (~${discounting_spend:,.0f} in spend exposed). "
    f"At {demand_retention}% assumed demand retention and {discount_depth}% discount depth, "
    f"the model estimates margin recovered on retained spend minus revenue lost from churned demand."
)

st.markdown("---")

# ============================================================================
# COMPARISON ACROSS SEGMENTS (bar)
# ============================================================================
st.subheader("Discount Reliance by Segment")
fig = px.bar(
    seg_summary, x='Customer_Segment', y='pct_using_discount', color='Customer_Segment',
    color_discrete_map=SEGMENT_COLORS, text_auto='.1f',
    category_orders={'Customer_Segment': SEGMENT_ORDER},
    labels={'pct_using_discount': '% Using Discount', 'Customer_Segment': ''}
)
fig.update_layout(showlegend=False, height=380, margin=dict(t=10, b=10))
st.plotly_chart(fig, use_container_width=True)
