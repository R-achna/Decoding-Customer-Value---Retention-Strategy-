import streamlit as st
import plotly.express as px
from utils import load_data, sidebar_filters, ENGAGEMENT_ORDER

st.set_page_config(page_title="Category Analysis", page_icon="👕", layout="wide")

df = load_data()
filtered = sidebar_filters(df, key_prefix="category")

st.title("👕 Category Funnel")
st.caption("Entry-point vs. retention categories, and how tenure and season interact with product category.")

# ============================================================================
# CATEGORY VS TENURE
# ============================================================================
st.subheader("Category vs. Customer Tenure")

cat_summary = (
    filtered.groupby('Category', observed=True)
    .agg(customers=('Customer ID', 'count'), avg_previous_purchases=('Previous Purchases', 'mean'))
    .reset_index().sort_values('avg_previous_purchases', ascending=False)
)
cat_tier = filtered.groupby(['Category', 'Engagement_Depth_Tier'], observed=True).size().reset_index(name='count')

c1, c2 = st.columns(2)
with c1:
    fig_a = px.bar(cat_summary, x='Category', y='avg_previous_purchases', color='Category', text_auto='.1f')
    fig_a.update_layout(height=380, showlegend=False, margin=dict(t=10, b=10), yaxis_title="Avg. Previous Purchases")
    st.plotly_chart(fig_a, use_container_width=True)
with c2:
    fig_b = px.bar(cat_tier, x='Category', y='count', color='Engagement_Depth_Tier', barmode='stack',
                    category_orders={'Engagement_Depth_Tier': ENGAGEMENT_ORDER})
    fig_b.update_layout(height=380, margin=dict(t=10, b=10), yaxis_title="Customers")
    st.plotly_chart(fig_b, use_container_width=True)

st.caption("💡 Differences across categories are small in this dataset — category alone isn't a strong retention lever here.")
st.markdown("---")

# ============================================================================
# CATEGORY x SEASON HEATMAP
# ============================================================================
st.subheader("Category × Season — Tenure Heatmap")

pivot = filtered.pivot_table(
    index='Category', columns='Season', values='Previous Purchases', aggfunc='mean'
).reindex(columns=['Winter', 'Spring', 'Summer', 'Fall'])

fig_heat = px.imshow(
    pivot.round(1), text_auto=True, aspect='auto', color_continuous_scale='Blues',
    labels=dict(color="Avg. Previous Purchases")
)
fig_heat.update_layout(height=350, margin=dict(t=10, b=10))
st.plotly_chart(fig_heat, use_container_width=True)
st.caption("💡 Look for genuine hot/cold spots vs. uniform color — a flat-looking grid here (as expected from EDA) means season × category isn't a meaningful targeting axis.")

st.markdown("---")

# ============================================================================
# ITEM-LEVEL DRILL-DOWN
# ============================================================================
st.subheader("Top Items by Category")
selected_cat = st.selectbox("Select category:", sorted(filtered['Category'].unique()))
item_summary = (
    filtered[filtered['Category'] == selected_cat]
    .groupby('Item Purchased', observed=True)
    .agg(customers=('Customer ID', 'count'), avg_spend=('Purchase Amount (USD)', 'mean'))
    .reset_index().sort_values('customers', ascending=False)
)
st.dataframe(item_summary.round(1), use_container_width=True, hide_index=True)
