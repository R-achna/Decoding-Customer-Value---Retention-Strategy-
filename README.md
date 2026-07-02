## Decoding Customer Value: A SQL-Driven Retention Strategy

A direct-to-consumer fashion brand with about 3,900 customers has been running a discount program without ever testing whether it actually builds loyalty. This project answers that question using only transactional and behavioral data.

Live dashboard: https://hsth3a365aygffvharjx3r.streamlit.app/

### Problem Statement

Using only transactional and behavioral data, identify what the brand's most valuable customers look like, measure how much of current revenue depends on promotions, and build a data-backed retention strategy that reduces discount dependency without hurting sales.

Two constraints shaped everything that follows. The dataset has no existing loyalty score, churn flag, or timestamps, so every concept used here, loyalty, value, discount reliance, had to be defined and defended from raw variables rather than pulled from a label that already existed. And loyalty specifically had to be built as at least two competing definitions, tested against each other, rather than declared outright.

### About the Dataset

Source: Customer Shopping Trends Dataset, Kaggle.

3,900 rows, one row per customer. Kaggle documents this as synthetic data, built for practicing customer analytics rather than pulled from a real retailer's systems. That distinction matters here. A few patterns in the data, the gender split in discount usage, the disconnect between stated purchase frequency and actual purchase count, are almost certainly artifacts of how the data was generated rather than real consumer behavior. Both are identified and worked around in the cleaning process below, but it's worth naming upfront rather than letting the numbers imply this is live transaction data from an actual brand.

Columns as provided: Customer ID, Age, Gender, Item Purchased, Category, Purchase Amount, Location, Size, Color, Season, Review Rating, Subscription Status, Shipping Type, Discount Applied, Promo Code Used, Previous Purchases, Payment Method, Frequency of Purchases.

### Process and Methodology

The work moves through three stages, each building on the last.

Python handles cleaning and feature engineering. This is where the data gets audited for structural problems, where every metric used later gets built and justified, and where the two competing loyalty definitions get constructed and compared.

SQL handles segmentation. Once the customer-level features exist, SQL answers each of the brand's core strategic questions by grouping and aggregating across the segments built in the Python stage.

Streamlit turns the findings into something a non-technical founding team can actually use, with filters, drill-downs into individual customers, and a what-if simulator for the promotional recommendation.

Each stage produces something that feeds the next one. Nothing in the SQL layer or the dashboard is calculated independently of the feature engineering, everything traces back to a decision made and explained in the Python stage.

### Repository Structure

```
.devcontainer/      environment config for Codespaces
dashboard/          the Streamlit app (app.py, pages/, data/, utils.py)
notebooks/          Python cleaning and feature engineering, exported from Kaggle
sql/                the segmentation queries that answer the questions below
rawdata/            the original, untouched dataset
```

### Tools Used

Python (pandas) for cleaning, auditing, and feature engineering. statsmodels for the regression testing that ruled Frequency of Purchases in or out of the loyalty score. DuckDB for the SQL segmentation layer, chosen over a full database server since it reads a CSV directly with no setup. Streamlit and Plotly for the interactive dashboard. Kaggle Notebooks as the development environment for the Python and SQL work. GitHub for version control and hosting, Streamlit Community Cloud for deployment.

### What Got Caught in Cleaning

Two things surfaced early that changed the rest of the approach.

Discount usage isn't really a behavioral signal in this dataset. Every female customer shows zero discount usage, about 63% of male customers show it, and 100% of subscribers show it. That's a property of how the data was generated, not a reflection of real customer choice. So any discount reliance metric used from here on ranks usage within gender instead of taking it at face value.

Stated purchase frequency also turned out to carry no real information. A regression of actual purchase count against stated frequency, controlling for age, gender, and category, came back with no significant relationship (p = 0.118). About one in ten customers even show a frequency label that contradicts their purchase count, someone marked "Annually" with over 30 previous purchases. That field got left out of every score built afterward.

### How Loyalty Is Defined

Two scores, built from different things on purpose, so they'd disagree in places that matter.

Behavioral loyalty uses purchase history alone, since that was the only field that held up under testing.

Value and satisfaction loyalty combines estimated lifetime spend with review rating, asking a different question: is this relationship actually good, not just long.

Crossing the two gives four groups. Core Loyal (high on both), Habitual But Not Yet Valuable (long history, lower value or satisfaction), Promising New (high value, shorter history), and Low Priority (low on both).

---

### SQL Analysis

Each question below is taken directly from the project brief. Query first, then what came back, then what it means.

#### What separates high-value customers from low-value ones, and which profiles show the strongest repeat purchase behavior?

```sql
SELECT
    "Value_Tier",
    COUNT(*) AS customer_count,
    ROUND(AVG("Estimated_Lifetime_Spend"), 0) AS avg_lifetime_spend,
    ROUND(AVG("Previous Purchases"), 1) AS avg_previous_purchases,
    ROUND(
        100.0 * SUM(CASE WHEN "Engagement_Depth_Tier" = 'Veteran' THEN 1 ELSE 0 END) / COUNT(*),
        1
    ) AS pct_veteran_tenure
FROM customers
GROUP BY "Value_Tier"
ORDER BY avg_lifetime_spend DESC;
```

Platinum customers average $3,209 in lifetime spend and 39.6 previous purchases. Bronze customers average $368 and 8.5 purchases. Value and repeat purchase behavior move together here, but that's partly built in, since lifetime spend is calculated using purchase count as a multiplier. The real test of whether tenure independently predicts value comes later, once satisfaction gets crossed in.

#### Which seasons and categories are associated with lower-tenure customers versus those with high previous purchase counts?

```sql
SELECT "Category", ROUND(AVG("Previous Purchases"), 1) AS avg_previous_purchases
FROM customers
GROUP BY "Category"
ORDER BY avg_previous_purchases DESC;

SELECT "Season", ROUND(AVG("Previous Purchases"), 1) AS avg_previous_purchases
FROM customers
GROUP BY "Season"
ORDER BY avg_previous_purchases DESC;
```

Category averages range from 25.0 to 25.7 previous purchases. Season ranges just as tightly. Neither shows a meaningful split between low and high tenure customers. That's a genuine finding, just not the one people usually go looking for: category and season aren't useful retention levers in this dataset.

#### Which geographies signal organic demand versus discount-driven volume?

```sql
SELECT
    "Region",
    ROUND(AVG("Estimated_Lifetime_Spend"), 0) AS avg_spend,
    ROUND(AVG("Promo_Dependency_Score"), 3) AS avg_promo_dependency
FROM customers
GROUP BY "Region"
ORDER BY avg_spend DESC;
```

Regional spend ranges from $1,501 to $1,663. Promo dependency sits between 0.487 and 0.504 in every region, essentially the same everywhere. State-level numbers show more spread, but most states only have 60 to 90 customers behind them, too thin to build a market-by-market strategy on.

#### Who are the genuinely loyal customers vs. those who only buy when there is a discount?

```sql
SELECT
    "Customer_Segment",
    COUNT(*) AS customer_count,
    ROUND(AVG("Estimated_Lifetime_Spend"), 0) AS avg_spend,
    ROUND(100.0 * SUM("Discount Applied_Flag") / COUNT(*), 1) AS pct_using_discount,
    ROUND(AVG("Review Rating"), 2) AS avg_rating
FROM customers
GROUP BY "Customer_Segment"
ORDER BY avg_spend DESC;
```

| Segment | Customers | Avg. Spend | % Using Discount | Avg. Rating |
| --- | --- | --- | --- | --- |
| Core Loyal | 307 | $3,390 | 40.4% | 4.49% |
| Promising New | 219 | $2,485 | 42.9% | 4.72% |
| Habitual, Not Yet Valuable | 668 | $2,459 | 46.6% | 3.42% |
| Low Priority / At Risk | 2,706 | $1,081 | 42.4% | 3.69% |

This is the finding the rest of the project hangs off. The highest spending segment has the lowest discount usage in the base. The segment with the highest discount usage has the lowest satisfaction scores and middling spend. Loyalty and discount reliance run in opposite directions here.

#### What behavioral patterns today predict high customer value over time?

```sql
SELECT "Engagement_Depth_Tier", "Value_Tier", COUNT(*) AS customer_count
FROM customers
GROUP BY "Engagement_Depth_Tier", "Value_Tier";
```

Tenure alone isn't a reliable predictor. Plenty of long-tenured customers land in the lower value tiers once satisfaction gets factored in through the segment model above. The pattern that actually predicts value is the combination, sustained purchase history plus genuine satisfaction, not either one on its own.

#### Which geographies and demographics are commercially underlevered?

```sql
SELECT age_band, ROUND(AVG("Estimated_Lifetime_Spend"), 0) AS avg_spend
FROM customers
GROUP BY age_band
ORDER BY avg_spend DESC;
```

Age bands range from $1,521 to $1,657 in average spend, a 9% spread. Combined with the flat results across category, season, and region, the pattern across every demographic and geographic cut in this dataset is the same: none of them differentiate customers in a way that's useful for targeting.

#### How should the brand restructure its promotional strategy to protect margins without losing volume?

```sql
SELECT
    "Customer_Segment",
    ROUND(AVG("Promo_Dependency_Score"), 3) AS avg_promo_dependency,
    ROUND(100.0 * SUM("Discount Applied_Flag") / COUNT(*), 1) AS pct_using_discount
FROM customers
GROUP BY "Customer_Segment"
ORDER BY avg_promo_dependency DESC;
```

Habitual But Not Yet Valuable customers show both the highest discount usage and an already-proven purchase habit, making them the clearest candidate for a phased discount reduction, cut discount depth by roughly 30% for a test cohort, track repeat purchase rate and average order value against a control group over 60 to 90 days. Core Loyal customers need no change, they're already converting at the lowest discount rate in the base. Promising New customers should keep their discount for now, since it may still be doing real work getting a newer relationship established.

#### What does the brand's ideal customer profile look like, and how can it acquire more of them?

```sql
SELECT
    COUNT(*) AS n,
    ROUND(AVG("Age"), 1) AS avg_age,
    ROUND(AVG("Estimated_Lifetime_Spend"), 0) AS avg_spend,
    ROUND(AVG("Review Rating"), 2) AS avg_rating
FROM customers
WHERE "Customer_Segment" = 'Core Loyal';
```

The Core Loyal customer averages 44.3 previous purchases, a 4.49 rating, and $3,390 in lifetime spend, more than three times the base average. They buy mostly Clothing and Accessories. Age (43.9 average) and gender split (69% male, 31% female) both track the overall dataset almost exactly, meaning neither one is actually a useful signal for finding more customers like this. What defines this profile is behavior, not anything demographic.

---

### Limitations

This is a single snapshot with no dates attached, so anything called loyalty here is a propensity estimate based on current behavior, not something observed over time. The promo dependency score works around a data artifact rather than measuring something clean, and should be read with that in mind. State-level geographic claims are too thin on sample size to act on directly, which is why the regional rollups carry the actual conclusions.

This dataset is synthetic, generated for analytics practice rather than pulled from a real retailer's systems. The structural artifacts described above, discount usage tied to gender, purchase frequency uncorrelated with purchase history, are most likely generation quirks, not real consumer behavior, which is exactly why they were tested rather than trusted.

### Run Locally

```bash
cd dashboard
pip install -r requirements.txt
streamlit run app.py
```

---
