"""
Shared utilities for the multi-page dashboard: data loading, constants,
and consistent color mapping so every page looks/behaves the same way.
"""

import pandas as pd
import streamlit as st

SEGMENT_ORDER = ['Core Loyal', 'Habitual, Not Yet Valuable', 'Promising New', 'Low Priority / At Risk']
SEGMENT_COLORS = {
    'Core Loyal': '#2E7D32',
    'Habitual, Not Yet Valuable': '#F9A825',
    'Promising New': '#1E88E5',
    'Low Priority / At Risk': '#B0BEC5',
}

TIER_ORDER = ['Bronze', 'Silver', 'Gold', 'Platinum']
TIER_COLORS = {
    'Bronze': '#CD7F32', 'Silver': '#B0B0B0', 'Gold': '#D4AF37', 'Platinum': '#7C9CFF'
}

ENGAGEMENT_ORDER = ['New', 'Developing', 'Established', 'Veteran']

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

SEGMENT_ACTIONS = {
    'Core Loyal': 'Protect — already buying without discounts. Do not add promo spend here.',
    'Habitual, Not Yet Valuable': 'Sunset target — regular buyers, high discount reliance. Test discount reduction.',
    'Promising New': 'Nurture — newer relationship, discount may still be doing acquisition work.',
    'Low Priority / At Risk': 'Low investment — low behavioral and value signal on both fronts.',
}

from pathlib import Path

@st.cache_data
def load_data():
    data_path = Path(__file__).parent / "data" / "customer_features_engineered.csv"
    df = pd.read_csv(data_path)
    df['State_Abbr'] = df['Location'].map(STATE_ABBR)
    return df

def sidebar_filters(df, key_prefix=""):
    """Renders standard sidebar filters and returns the filtered dataframe.
    key_prefix keeps widget keys unique across pages."""
    st.sidebar.header("Filters")

    segment_filter = st.sidebar.multiselect(
        "Customer Segment",
        options=SEGMENT_ORDER,
        default=SEGMENT_ORDER,
        key=f"{key_prefix}_segment"
    )
    region_filter = st.sidebar.multiselect(
        "Region",
        options=sorted(df['Region'].dropna().unique()),
        default=sorted(df['Region'].dropna().unique()),
        key=f"{key_prefix}_region"
    )
    category_filter = st.sidebar.multiselect(
        "Category",
        options=sorted(df['Category'].unique()),
        default=sorted(df['Category'].unique()),
        key=f"{key_prefix}_category"
    )

    filtered = df[
        df['Customer_Segment'].isin(segment_filter) &
        df['Region'].isin(region_filter) &
        df['Category'].isin(category_filter)
    ]

    st.sidebar.markdown("---")
    st.sidebar.metric("Customers in view", f"{len(filtered):,}", f"of {len(df):,} total")
    return filtered
