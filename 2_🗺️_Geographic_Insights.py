import streamlit as st
import plotly.express as px
from utils import load_data, sidebar_filters

st.set_page_config(page_title="Geographic Insights", page_icon="🗺️", layout="wide")

df = load_data()
filtered = sidebar_filters(df, key_prefix="geo")

st.title("🗺️ Geographic Opportunity")
st.caption("Which states/regions show organic demand (high spend, low promo dependency) vs. discount-driven volume.")

# ============================================================================
# REGION-LEVEL COMPARISON
# ============================================================================
st.subheader("Region-Level Comparison")

region_summary = (
    filtered.groupby('Region', observed=True)
    .agg(customers=('Customer ID', 'count'),
         avg_spend=('Estimated_Lifetime_Spend', 'mean'),
         avg_promo_dependency=('Promo_Dependency_Score', 'mean'))
    .reset_index().sort_values('avg_spend', ascending=False)
)

r1, r2 = st.columns(2)
with r1:
    fig_r1 = px.bar(region_summary, x='Region', y='avg_spend', text_auto='.0f',
                     color='Region', labels={'avg_spend': 'Avg. Lifetime Spend ($)'})
    fig_r1.update_layout(showlegend=False, height=350, margin=dict(t=10, b=10))
    st.plotly_chart(fig_r1, use_container_width=True)
with r2:
    fig_r2 = px.bar(region_summary, x='Region', y='avg_promo_dependency', text_auto='.3f',
                     color='Region', labels={'avg_promo_dependency': 'Avg. Promo Dependency'})
    fig_r2.update_layout(showlegend=False, height=350, margin=dict(t=10, b=10))
    st.plotly_chart(fig_r2, use_container_width=True)

st.caption("💡 Region-level differences are modest across the board — no region stands out as dramatically over/underperforming.")
st.markdown("---")

# ============================================================================
# STATE-LEVEL MAP
# ============================================================================
st.subheader("State-Level Map")

geo_summary = (
    filtered.groupby(['Location', 'State_Abbr'], observed=True)
    .agg(customers=('Customer ID', 'count'),
         avg_spend=('Estimated_Lifetime_Spend', 'mean'),
         avg_promo_dependency=('Promo_Dependency_Score', 'mean'))
    .reset_index()
)

min_sample = st.slider("Minimum customers per state (filters out noisy small-sample states)", 5, 90, 15)
geo_stable = geo_summary[geo_summary['customers'] >= min_sample]

map_metric = st.radio("Color by:", ["Avg. Lifetime Spend", "Avg. Promo Dependency"], horizontal=True)
color_col = 'avg_spend' if map_metric == "Avg. Lifetime Spend" else 'avg_promo_dependency'
color_scale = 'Blues' if map_metric == "Avg. Lifetime Spend" else 'Oranges'

fig3 = px.choropleth(
    geo_stable, locations='State_Abbr', locationmode='USA-states', color=color_col,
    scope='usa', color_continuous_scale=color_scale,
    hover_data={'Location': True, 'customers': True, 'avg_spend': ':.0f', 'avg_promo_dependency': ':.3f'}
)
fig3.update_layout(height=450, margin=dict(t=10, b=10, l=0, r=0))
st.plotly_chart(fig3, use_container_width=True)
st.caption(f"Showing {len(geo_stable)} states with at least {min_sample} customers in the current filter.")

st.markdown("---")

# ============================================================================
# TOP/BOTTOM STATE TABLE
# ============================================================================
st.subheader("Top & Bottom States by Spend (stable sample sizes only)")
t1, t2 = st.columns(2)
stable_sorted = geo_summary[geo_summary['customers'] >= 60].sort_values('avg_spend', ascending=False)
with t1:
    st.markdown("**Top 8**")
    st.dataframe(stable_sorted.head(8).round(2), use_container_width=True, hide_index=True)
with t2:
    st.markdown("**Bottom 8**")
    st.dataframe(stable_sorted.tail(8).round(2), use_container_width=True, hide_index=True)
