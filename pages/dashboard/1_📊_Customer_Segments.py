import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from utils import load_data, sidebar_filters, SEGMENT_ORDER, SEGMENT_COLORS, TIER_ORDER, TIER_COLORS

st.set_page_config(page_title="Customer Segments", page_icon="📊", layout="wide")

df = load_data()
filtered = sidebar_filters(df, key_prefix="segments")

st.title("📊 Customer Segments")
st.caption("How value is distributed, who needs a discount to buy, and drill-down into individual customers.")

# ============================================================================
# PANEL 1 — CUSTOMER PYRAMID
# ============================================================================
st.subheader("Customer Pyramid — How Value is Distributed")

tier_summary = (
    filtered.groupby('Value_Tier', observed=True)
    .agg(customers=('Customer ID', 'count'), avg_spend=('Estimated_Lifetime_Spend', 'mean'))
    .reindex(TIER_ORDER).reset_index()
)

p1, p2 = st.columns([2, 1])
with p1:
    fig1 = go.Figure(go.Funnel(
        y=tier_summary['Value_Tier'], x=tier_summary['customers'],
        textinfo="value+percent total",
        marker={"color": [TIER_COLORS[t] for t in tier_summary['Value_Tier']]}
    ))
    fig1.update_layout(height=380, margin=dict(t=10, b=10))
    st.plotly_chart(fig1, use_container_width=True)
with p2:
    st.markdown("**Avg. Lifetime Spend by Tier**")
    for _, row in tier_summary.iterrows():
        st.metric(row['Value_Tier'], f"${row['avg_spend']:,.0f}")

st.caption("💡 Quartile-based on Estimated Lifetime Spend — roughly even population per tier by design; the spend gap is the story.")
st.markdown("---")

# ============================================================================
# PANEL 2 — PROMO DEPENDENCY VS VALUE
# ============================================================================
st.subheader("Promo Dependency vs. Value — Who Needs the Discount?")

seg_summary = (
    filtered.groupby('Customer_Segment', observed=True)
    .agg(customers=('Customer ID', 'count'),
         avg_promo_dependency=('Promo_Dependency_Score', 'mean'),
         avg_spend=('Estimated_Lifetime_Spend', 'mean'))
    .reindex(SEGMENT_ORDER).reset_index()
)

fig2 = px.scatter(
    seg_summary, x='avg_promo_dependency', y='avg_spend', size='customers',
    color='Customer_Segment', color_discrete_map=SEGMENT_COLORS, text='Customer_Segment',
    size_max=60,
    labels={'avg_promo_dependency': 'Avg. Promo Dependency (within-gender percentile)',
            'avg_spend': 'Avg. Lifetime Spend ($)'}
)
fig2.update_traces(textposition='top center')
fig2.update_layout(height=430, showlegend=False, margin=dict(t=10, b=10))
st.plotly_chart(fig2, use_container_width=True)
st.caption("💡 Core Loyal sits highest on spend, lowest on promo dependency — the headline finding of this analysis.")

st.markdown("---")

# ============================================================================
# DRILL-DOWN: individual customer rows by segment
# ============================================================================
st.subheader("🔍 Drill Down — Individual Customers")

drill_segment = st.selectbox("Select a segment to inspect:", SEGMENT_ORDER)

drill_df = filtered[filtered['Customer_Segment'] == drill_segment][[
    'Customer ID', 'Age', 'Gender', 'Category', 'Region', 'Location',
    'Purchase Amount (USD)', 'Previous Purchases', 'Review Rating',
    'Estimated_Lifetime_Spend', 'Value_Tier', 'Engagement_Depth_Tier',
    'Promo_Dependency_Score', 'Discount Applied'
]].sort_values('Estimated_Lifetime_Spend', ascending=False)

st.write(f"**{len(drill_df):,} customers** in *{drill_segment}* (within current filters)")
st.dataframe(drill_df, use_container_width=True, height=350)

csv = drill_df.to_csv(index=False).encode('utf-8')
st.download_button(
    f"⬇️ Download {drill_segment} customer list (CSV)",
    data=csv,
    file_name=f"{drill_segment.replace(' ', '_').replace(',', '')}_customers.csv",
    mime="text/csv"
)
