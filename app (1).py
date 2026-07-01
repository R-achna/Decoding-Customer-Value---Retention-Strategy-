import streamlit as st
from utils import load_data, sidebar_filters, SEGMENT_ORDER, SEGMENT_COLORS
import plotly.express as px

st.set_page_config(page_title="Overview | Customer Value Dashboard", page_icon="🏠", layout="wide")

df = load_data()
filtered = sidebar_filters(df, key_prefix="home")

st.title("🏠 Customer Value & Retention — Overview")
st.caption(
    "Is this business building genuine customer loyalty, or is it reliant on "
    "continuous promotional activity? Use the sidebar to filter, and the pages "
    "on the left to explore segments, geography, category, and the promotional "
    "sunset plan in depth."
)

# ============================================================================
# KPI ROW
# ============================================================================
c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Total Customers", f"{len(filtered):,}")
c2.metric("Avg. Lifetime Spend", f"${filtered['Estimated_Lifetime_Spend'].mean():,.0f}")
c3.metric("Avg. Review Rating", f"{filtered['Review Rating'].mean():.2f} / 5")
core_pct = (filtered['Customer_Segment'] == 'Core Loyal').mean() * 100
c4.metric("% Core Loyal", f"{core_pct:.1f}%")
discount_pct = filtered['Discount Applied_Flag'].mean() * 100
c5.metric("% Using Discounts", f"{discount_pct:.1f}%")

st.markdown("---")

# ============================================================================
# KEY INSIGHTS PANEL
# ============================================================================
st.subheader("💡 Key Insights")

seg_stats = filtered.groupby('Customer_Segment', observed=True).agg(
    n=('Customer ID', 'count'),
    avg_spend=('Estimated_Lifetime_Spend', 'mean'),
    avg_promo=('Promo_Dependency_Score', 'mean')
)

insight_col1, insight_col2 = st.columns(2)

with insight_col1:
    st.markdown("""
    **1. Loyalty isn't built on discounts.**
    Core Loyal customers — the highest-spending segment — show the *lowest*
    discount dependency of any group. They don't need a promo code to keep
    buying.

    **2. The biggest segment isn't the most valuable one.**
    "Habitual, Not Yet Valuable" customers (regular buyers, lower spend/satisfaction)
    are both the most discount-reliant *and* one of the largest segments —
    the clearest target for a promotional sunset test.
    """)

with insight_col2:
    st.markdown("""
    **3. Demographics and geography aren't the story here.**
    Age, region, category, and season all show flat, non-differentiating
    patterns in this dataset. What actually separates customers is
    **behavior** — purchase history and satisfaction — not who they are or
    where they live.

    **4. ~10% of customer profiles show a data inconsistency**
    (e.g., "Annually" purchasers with 30+ previous purchases) — flagged and
    excluded from scoring rather than silently trusted. See the Methodology
    page for the full data quality writeup.
    """)

st.markdown("---")

# ============================================================================
# SEGMENT SNAPSHOT CHART
# ============================================================================
st.subheader("Segment Snapshot")

seg_df = seg_stats.reindex(SEGMENT_ORDER).reset_index()
fig = px.bar(
    seg_df, x='Customer_Segment', y='n', color='Customer_Segment',
    color_discrete_map=SEGMENT_COLORS,
    text='n',
    category_orders={'Customer_Segment': SEGMENT_ORDER},
    labels={'n': 'Customers', 'Customer_Segment': ''}
)
fig.update_layout(showlegend=False, height=380, margin=dict(t=10, b=10))
st.plotly_chart(fig, use_container_width=True)

st.info(
    "👉 Head to **Customer Segments** in the sidebar to drill into each segment's "
    "individual customers, or **Promo Sunset Plan** for the specific recommendation "
    "and a what-if revenue simulator."
)
