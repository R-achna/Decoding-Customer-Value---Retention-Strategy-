# Decoding Customer Value — Founder Dashboard (Multi-Page)

An interactive, multi-page Streamlit dashboard for a D2C fashion brand's
founding team, answering: **is the business building genuine customer
loyalty, or is it reliant on continuous promotional activity?**

## Pages

- **🏠 Overview** — KPIs and headline insights at a glance
- **📊 Customer Segments** — value pyramid, promo-dependency-vs-value scatter,
  and a drill-down table of individual customers per segment (with CSV export)
- **🗺️ Geographic Insights** — region comparison and an interactive state-level
  map, with an adjustable minimum sample size to filter out noisy small states
- **👕 Category Analysis** — category/tenure funnel, a category × season
  tenure heatmap, and top-item drill-down
- **💰 Promo Sunset Plan** — the actual recommendation by segment, plus a
  what-if simulator for estimating margin impact of a discount reduction
  (clearly labeled as illustrative — the dataset has no true margin data)
- **📋 Methodology** — full feature dictionary and data limitations, so every
  number on every page can be traced back to its logic and caveats

## Run locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

Opens at `http://localhost:8501`. Multi-page navigation appears automatically
in the sidebar — no extra config needed.

## Deploying to Streamlit Community Cloud

1. Push this entire folder to a public GitHub repo (structure must be preserved —
   `app.py` at root, `pages/` folder alongside it, `data/` folder with the CSV).
2. Go to [share.streamlit.io](https://share.streamlit.io), connect your repo.
3. Set main file path to `app.py`.
4. Deploy.

## Data

`data/customer_features_engineered.csv` — 3,900 customers, cleaned and
feature-engineered from a synthetic D2C fashion retail dataset. See the
Methodology page in the app for the full logic behind every engineered column.

## Key finding

Customers in the highest-value segment ("Core Loyal") show the *lowest*
discount dependency of any segment — the brand's most valuable customers
don't need promotions to keep buying. Lower-value, habitual customers are
the most discount-reliant, making them the primary candidate for a
promotional sunset test (see the Promo Sunset Plan page for the full
recommendation and simulator).
