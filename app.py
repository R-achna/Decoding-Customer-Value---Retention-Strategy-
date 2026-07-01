"""
Decoding Customer Value — Founder Dashboard
A four-panel Streamlit dashboard for a non-technical D2C fashion brand
founding team, built on top of the engineered customer feature set.

Run locally with:  streamlit run app.py
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ============================================================================
# PAGE CONFIG
# ============================================================================
st.set_page_config(
    page_title="Customer Value & Retention Dashboard",
    page_icon="📊",
    layout="wide",
)

# ============================================================================
# DATA LOADING
# ============================================================================
@st.cache_data
def load_data():
    df = pd.read_csv("data/customer_features_engineered.csv")
    return df

df = load_data()

# US state -> region mapping for the geographic panel (same logic as the
# Python feature engineering step, kept here for map plotting)
STATE_ABBR = {
    'Alabama':'AL','Alaska':'AK','Arizona':'AZ','Arkansas':'AR','California':'CA',
    'Colorado':'CO','Connecticut':'CT','Delaware':'DE','Florida':'FL','Georgia':'GA',
    'Hawaii':'HI','Idaho':'ID','Illinois':'IL','Indiana':'IN','Iowa':'IA','Kansas':'KS',
    'Kentucky':'KY','Louisiana':'LA','Maine':'ME','Maryland':'MD','Massachusetts':'MA',
    'Michigan':'MI','Minnesota':'MN','Mississippi':'MS','Missouri':'MO','Montana':'MT',
    'Nebraska':'NE','Nevada':'NV','New Hampshire':'NH','New Jersey':'NJ','New Mexico':'NM',
    'New York':'NY','North Carolina':'NC','North Dakota':'ND','Ohio':'OH','Oklahoma':'OK',
    'Oregon':'OR','Pennsylvania':'PA','Rhode Island':'RI','South Carolina':'SC',
    'South Dakota':'SD','Tennessee':'TN','Texas':'TX','Utah':'UT','Vermont':'VT',
    'Virginia':'VA','Washington':'WA','West Virginia':'WV','Wisconsin':'WI','Wyoming':'WY'
}
df['State_Abbr'] = df['Location'].map(STATE_ABBR)

# ============================================================================
# SIDEBAR — FILTERS (lets a founder slice the whole dashboard interactively)
# ============================================================================
st.sidebar.header("Filters")

segment_filter = st.sidebar.multiselect(
    "Customer Segment",
    options=sorted(df['Customer_Segment'].unique()),
    default=sorted(df['Customer_Segment'].unique())
)

region_filter = st.sidebar.multiselect(
    "Region",
    options=sorted(df['Region'].dropna().unique()),
    default=sorted(df['Region'].dropna().unique())
)

category_filter = st.sidebar.multiselect(
    "Category",
    options=sorted(df['Category'].unique()),
    default=sorted(df['Category'].unique())
)

filtered = df[
    df['Customer_Segment'].isin(segment_filter) &
    df['Region'].isin(region_filter) &
    df['Category'].isin(category_filter)
]

st.sidebar.markdown("---")
st.sidebar.metric("Customers in view", f"{len(filtered):,}", f"of {len(df):,} total")

# ============================================================================
# HEADER + KEY METRICS ROW
# ============================================================================
st.title("📊 Decoding Customer Value: Founder Dashboard")
st.caption(
    "Is the business building genuine loyalty, or renting it with discounts? "
    "Use the filters on the left to explore by segment, region, and category."
)

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Customers", f"{len(filtered):,}")
col2.metric("Avg. Lifetime Spend", f"${filtered['Estimated_Lifetime_Spend'].mean():,.0f}")
col3.metric("Avg. Review Rating", f"{filtered['Review Rating'].mean():.2f} / 5")
core_loyal_pct = (filtered['Customer_Segment'] == 'Core Loyal').mean() * 100
col4.metric("% Core Loyal", f"{core_loyal_pct:.1f}%")

st.markdown("---")

# ============================================================================
# PANEL 1 — CUSTOMER PYRAMID
# ============================================================================
st.subheader("1️⃣ Customer Pyramid — How Value is Distributed")

tier_order = ['Bronze', 'Silver', 'Gold', 'Platinum']
tier_summary = (
    filtered.groupby('Value_Tier', observed=True)
    .agg(customers=('Customer ID', 'count'),
         avg_spend=('Estimated_Lifetime_Spend', 'mean'))
    .reindex(tier_order)
    .reset_index()
)

p1_col1, p1_col2 = st.columns([2, 1])

with p1_col1:
    fig1 = go.Figure(go.Funnel(
        y=tier_summary['Value_Tier'],
        x=tier_summary['customers'],
        textinfo="value+percent total",
        marker={"color": ["#CD7F32", "#B0B0B0", "#D4AF37", "#7C9CFF"]}
    ))
    fig1.update_layout(height=400, margin=dict(t=10, b=10))
    st.plotly_chart(fig1, use_container_width=True)

with p1_col2:
    st.markdown("**Avg. Lifetime Spend by Tier**")
    for _, row in tier_summary.iterrows():
        st.metric(row['Value_Tier'], f"${row['avg_spend']:,.0f}")

st.caption(
    "💡 Value tiers are quartile-based on Estimated Lifetime Spend "
    "(order value × previous purchases). Roughly even population per tier "
    "by design — the spend gap between tiers is where the real story is."
)

st.markdown("---")

# ============================================================================
# PANEL 2 — PROMO DEPENDENCY VS. RETENTION
# ============================================================================
st.subheader("2️⃣ Promo Dependency vs. Customer Value — Who Needs the Discount?")

segment_summary = (
    filtered.groupby('Customer_Segment', observed=True)
    .agg(customers=('Customer ID', 'count'),
         avg_promo_dependency=('Promo_Dependency_Score', 'mean'),
         avg_spend=('Estimated_Lifetime_Spend', 'mean'),
         pct_using_discount=('Discount Applied_Flag', 'mean'))
    .reset_index()
)
segment_summary['pct_using_discount'] *= 100

fig2 = px.scatter(
    segment_summary,
    x='avg_promo_dependency',
    y='avg_spend',
    size='customers',
    color='Customer_Segment',
    text='Customer_Segment',
    size_max=60,
    labels={
        'avg_promo_dependency': 'Avg. Promo Dependency Score (within-gender percentile)',
        'avg_spend': 'Avg. Lifetime Spend ($)'
    }
)
fig2.update_traces(textposition='top center')
fig2.update_layout(height=450, showlegend=False, margin=dict(t=10, b=10))
st.plotly_chart(fig2, use_container_width=True)

st.caption(
    "💡 **Key finding:** Core Loyal customers sit at the highest spend but "
    "*lowest* promo dependency — they don't need a discount to keep buying. "
    "'Habitual, Not Yet Valuable' customers are the most discount-reliant "
    "despite lower spend, making them the primary candidate for the "
    "promotional sunset plan."
)

st.markdown("---")

# ============================================================================
# PANEL 3 — GEOGRAPHIC OPPORTUNITY MAP
# ============================================================================
st.subheader("3️⃣ Geographic Opportunity — Organic Demand vs. Discount-Driven")

geo_summary = (
    filtered.groupby(['Location', 'State_Abbr'], observed=True)
    .agg(customers=('Customer ID', 'count'),
         avg_spend=('Estimated_Lifetime_Spend', 'mean'),
         avg_promo_dependency=('Promo_Dependency_Score', 'mean'))
    .reset_index()
)
geo_summary_stable = geo_summary[geo_summary['customers'] >= 15]  # small-sample guard for the filtered view

map_metric = st.radio(
    "Map by:", ["Avg. Lifetime Spend", "Avg. Promo Dependency"],
    horizontal=True
)
color_col = 'avg_spend' if map_metric == "Avg. Lifetime Spend" else 'avg_promo_dependency'
color_scale = 'Blues' if map_metric == "Avg. Lifetime Spend" else 'Oranges'

fig3 = px.choropleth(
    geo_summary_stable,
    locations='State_Abbr',
    locationmode='USA-states',
    color=color_col,
    scope='usa',
    color_continuous_scale=color_scale,
    hover_data={'Location': True, 'customers': True, 'avg_spend': ':.0f', 'avg_promo_dependency': ':.3f'}
)
fig3.update_layout(height=450, margin=dict(t=10, b=10, l=0, r=0))
st.plotly_chart(fig3, use_container_width=True)

st.caption(
    "💡 Regional differences in this dataset are modest — no single region "
    "or state shows dramatic over/under-performance. States shown require "
    "at least 15 customers in the current filter to reduce small-sample noise. "
    "Treat any single state as a directional signal, not a confirmed pattern."
)

st.markdown("---")

# ============================================================================
# PANEL 4 — CATEGORY FUNNEL
# ============================================================================
st.subheader("4️⃣ Category Funnel — Entry-Point vs. Retention Categories")

cat_summary = (
    filtered.groupby('Category', observed=True)
    .agg(customers=('Customer ID', 'count'),
         avg_previous_purchases=('Previous Purchases', 'mean'))
    .reset_index()
    .sort_values('avg_previous_purchases', ascending=False)
)

cat_tier = (
    filtered.groupby(['Category', 'Engagement_Depth_Tier'], observed=True)
    .size().reset_index(name='count')
)

p4_col1, p4_col2 = st.columns(2)

with p4_col1:
    fig4a = px.bar(
        cat_summary, x='Category', y='avg_previous_purchases',
        color='Category', text_auto='.1f'
    )
    fig4a.update_layout(height=380, showlegend=False, margin=dict(t=10, b=10),
                         yaxis_title="Avg. Previous Purchases")
    st.plotly_chart(fig4a, use_container_width=True)

with p4_col2:
    fig4b = px.bar(
        cat_tier, x='Category', y='count', color='Engagement_Depth_Tier',
        barmode='stack',
        category_orders={'Engagement_Depth_Tier': ['New', 'Developing', 'Established', 'Veteran']}
    )
    fig4b.update_layout(height=380, margin=dict(t=10, b=10), yaxis_title="Customers")
    st.plotly_chart(fig4b, use_container_width=True)

st.caption(
    "💡 Differences in tenure across categories are small in this dataset — "
    "no category stands out sharply as a clear entry-point vs. retention "
    "driver. This itself is a finding: category alone is not a strong "
    "lever for retention strategy here."
)

st.markdown("---")

# ============================================================================
# FOOTER — METHODOLOGY NOTES
# ============================================================================
with st.expander("📋 Methodology & Data Limitations"):
    st.markdown("""
    - **Estimated Lifetime Spend** = observed order value × (previous purchases + 1).
      Assumes the observed order is representative of typical order size.
    - **Loyalty Score A (Behavioral)** is built solely from *Previous Purchases* —
      validated as the only field with real predictive relationship to purchase
      history (Frequency of Purchases and Subscription Status were tested and
      showed no significant relationship, p > 0.1, and were excluded to avoid
      diluting the score with noise).
    - **Loyalty Score B (Value + Satisfaction)** combines Estimated Lifetime
      Spend and Review Rating.
    - **Customer Segment** is a four-quadrant label from Loyalty A × Loyalty B
      (top-25% thresholds on each).
    - **Promo Dependency Score** is ranked *within gender*, since raw discount
      usage in this dataset is structurally tied to Gender and Subscription
      Status (0% for Female customers, 100% when subscribed) rather than
      reflecting genuine behavioral choice.
    - ~2% of customers sit at the maximum recorded tenure (50 previous
      purchases) — their true tenure may be understated (censoring).
    - This dashboard uses a single-snapshot dataset (no timestamps); all
      "loyalty" and "value" measures are current-state proxies, not
      observed retention over time.
    """)

st.caption("Built with Streamlit · Data: synthetic D2C fashion brand customer dataset (3,900 customers)")
