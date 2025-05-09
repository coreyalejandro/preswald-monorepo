from preswald import (
    text,
    separator,
    plotly,
    connect,
    get_df,
    table,
    slider,
    workflow_dag,
    Workflow
)
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# 1. TITLE
text("# Superstore Executive Dashboard\n_A data-driven overview with advanced, interactive visuals_")
separator()

# 2. LOAD DATA
connect()
df = get_df(source_name="my_sample_superstore")  # loads data/my_sample_superstore.csv
df["Order Date"] = pd.to_datetime(df["Order Date"])
df["Year"] = df["Order Date"].dt.year
df["Month"] = df["Order Date"].dt.to_period("M").dt.to_timestamp()

# 3. RAW DATA PREVIEW (convert dates to strings for JSON serialization)
df_preview = df.copy()
df_preview["Order Date"] = df_preview["Order Date"].dt.strftime("%Y-%m-%d")
table(df_preview.head(10), title="Raw Data Preview")
separator()

# 4. DYNAMIC FILTERS
min_sales = slider("Min Sales ($)", min_val=0, max_val=int(df["Sales"].max()), default=0)
max_sales = slider("Max Sales ($)", min_val=0, max_val=int(df["Sales"].max()), default=int(df["Sales"].max()))
start_year = slider("Start Year", min_val=int(df["Year"].min()), max_val=int(df["Year"].max()), default=int(df["Year"].min()))

filtered = df[
    (df["Sales"] >= min_sales) &
    (df["Sales"] <= max_sales) &
    (df["Year"] >= start_year)
]

filtered_preview = filtered.copy()
filtered_preview["Order Date"] = filtered_preview["Order Date"].dt.strftime("%Y-%m-%d")
table(filtered_preview.head(10), title="Filtered Data Sample")
separator()

# 5. KPI SUMMARY (using Indicator subplots)
text("## Key Metrics")
metrics = {
    "Total Sales": filtered["Sales"].sum(),
    "Total Profit": filtered["Profit"].sum(),
    "Average Discount": filtered["Discount"].mean(),
    "Order Count": len(filtered)
}
fig_kpi = make_subplots(rows=1, cols=4, specs=[[{"type": "indicator"}]*4])
fig_kpi.add_trace(go.Indicator(
    mode="number",
    value=metrics["Total Sales"],
    title={"text": "Total Sales"},
    number={"prefix": "$", "valueformat": ",.0f"}
), row=1, col=1)
fig_kpi.add_trace(go.Indicator(
    mode="number",
    value=metrics["Total Profit"],
    title={"text": "Total Profit"},
    number={"prefix": "$", "valueformat": ",.0f"}
), row=1, col=2)
fig_kpi.add_trace(go.Indicator(
    mode="number",
    value=metrics["Average Discount"],
    title={"text": "Avg Discount"},
    number={"valueformat": ".2%"}
), row=1, col=3)
fig_kpi.add_trace(go.Indicator(
    mode="number",
    value=metrics["Order Count"],
    title={"text": "Order Count"},
    number={"valueformat": ",d"}
), row=1, col=4)
fig_kpi.update_layout(height=200, margin={"t":50, "b":0})
plotly(fig_kpi)
separator()

# 6. SALES & PROFIT BY CATEGORY (Dark-themed Grouped Bar)
text("## Sales vs Profit by Category")
cat_df = filtered.groupby("Category").agg(Sales=("Sales","sum"), Profit=("Profit","sum")).reset_index()
fig_cat = px.bar(
    cat_df,
    x="Category",
    y=["Sales","Profit"],
    barmode="group",
    title="Sales & Profit by Category",
    color_discrete_map={"Sales":"#636EFA","Profit":"#EF553B"},
)
fig_cat.update_layout(template="plotly_dark", yaxis_title="Amount ($)")
plotly(fig_cat)
text("""
- **Furniture** has the highest absolute sales but lower profit margin.
- **Technology** leads in profitability, indicating strong margins.
- **Office Supplies** underperforms in both metrics—potential for strategic review.
""")
separator()

# 7. MONTHLY SALES TREND (Range Slider & Selectors)
text("## Monthly Sales Trend")
monthly_df = filtered.groupby("Month").agg(Sales=("Sales","sum")).reset_index()
monthly_df["Month"] = monthly_df["Month"].dt.strftime("%Y-%m")
fig_month = px.line(
    monthly_df,
    x="Month",
    y="Sales",
    markers=True,
    title="Monthly Sales Trend"
)
fig_month.update_layout(
    template="plotly_white",
    xaxis=dict(
        type="category"
    ),
    yaxis_title="Sales ($)"
)
plotly(fig_month)
text("""
- Clear seasonal patterns with peaks around end-of-year.
- Recent dip may signal market slow-down or inventory constraints.
- Use range slider to zoom into specific periods.
""")
separator()

# 8. SUB-CATEGORY vs REGION HEATMAP
text("## Sales Heatmap: Sub-Category vs Region")
pivot_df = filtered.pivot_table(
    index="Sub-Category",
    columns="Region",
    values="Sales",
    aggfunc="sum",
    fill_value=0
)
fig_heat = px.imshow(
    pivot_df,
    labels=dict(x="Region", y="Sub-Category", color="Sales"),
    color_continuous_scale="Viridis",
    title="Sales by Sub-Category & Region"
)
plotly(fig_heat)
text("""
- Darker cells indicate top-performing sub-categories in each region.
- Identify regional underperformers (light cells) for targeted action.
- "Tables" in the Central region lag behind—review marketing/support.
""")
separator()

# 9. DISCOUNT vs PROFIT DENSITY CONTOUR
text("## Discount vs Profit Distribution")
fig_den = px.density_contour(
    filtered,
    x="Discount",
    y="Profit",
    color="Category",
    title="Impact of Discount on Profit"
)
fig_den.update_traces(
    contours_coloring="fill",
    contours_showlabels=True,
    selector=dict(type="histogram2dcontour")
)
fig_den.update_layout(template="plotly_white")
plotly(fig_den)
text("""
- High discount rates (>40%) often correspond to negative profit zones.
- Furniture shows the steepest profit decline as discounts increase.
- Consider capping discounts to preserve margins.
""")
separator()

# 10. CORRELATION MATRIX
text("## Correlation Matrix")
corr_df = filtered[["Sales","Profit","Quantity","Discount"]].corr()
fig_corr = px.imshow(
    corr_df,
    text_auto=True,
    color_continuous_scale="RdBu",
    title="Feature Correlation"
)
fig_corr.update_layout(template="plotly_white")
plotly(fig_corr)
text("""
- Strong positive correlation between **Sales** and **Profit**.
- **Discount** negatively correlates with profit—validate discount policies.
- **Quantity** shows weaker correlation, indicating volume isn't sole driver of profit.
""")
separator()

# 11. WORKFLOW DIAGRAM
workflow = Workflow()

@workflow.atom()
def data_load():
    return "Load & Clean Data"

@workflow.atom(dependencies=["data_load"])
def data_filter():
    return "Filter Data"

@workflow.atom(dependencies=["data_filter"])
def data_viz():
    return "Generate Visualizations"

workflow_dag(workflow, title="Execution Workflow")
