df_original = pd.read_csv("data/my_sample_superstore.csv")
df_original["Order Date"] = pd.to_datetime(df_original["Order Date"])
df_original["Profit Margin"] = df_original["Profit"] / df_original["Sales"]
df_original['State_Code'] = df_original['State'].map(state_abbrev)
import pandas as pd
import plotly.express as px
from preswald import connect, get_df, text, table, plotly

# Initialize connection and load data
connect()
df = get_df("my_sample_superstore")
df["Order Date"] = pd.to_datetime(df["Order Date"])
df["Profit Margin"] = df["Profit"] / df["Sales"]

# ─── Merchandising Visualizations (Codex p14-15) ─────────────────────────
text("# 📊 Superstore Merchandising Analysis")
text("## Codex p14-15 Reproduced Visualizations")

# 1. Sales by Category
cat_sales = df.groupby("Category", as_index=False)["Sales"].sum()
fig1 = px.bar(cat_sales, x="Category", y="Sales", title="Sales by Category")
plotly(fig1)

# 2. Market Share by Segment
seg_sales = df.groupby("Segment", as_index=False)["Sales"].sum()
fig2 = px.pie(seg_sales, names="Segment", values="Sales", title="Market Share by Segment")
plotly(fig2)

# 3. Profit Trend Over Time
profit_trend = df.resample("M", on="Order Date")["Profit"].sum().reset_index()
fig3 = px.line(profit_trend, x="Order Date", y="Profit", title="Profit Trend Over Time")
plotly(fig3)

# 4. Stacked Sales by Region and Category
reg_cat = df.groupby(["Region", "Category"], as_index=False)["Sales"].sum()
fig4 = px.bar(reg_cat, x="Region", y="Sales", color="Category", barmode="stack",
             title="Sales by Region and Category")
plotly(fig4)

# 5. Profitability Heatmap: Sub-Category vs Region
heat_data = df.groupby(["Region", "Sub-Category"], as_index=False)["Profit"].sum()
heat_pivot = heat_data.pivot(index="Region", columns="Sub-Category", values="Profit").fillna(0)
fig5 = px.imshow(heat_pivot,
                labels=dict(x="Sub-Category", y="Region", color="Profit"),
                title="Profitability by Sub-Category and Region")
plotly(fig5)

# 6. Sales vs Profit Scatter
fig6 = px.scatter(df, x="Sales", y="Profit", title="Sales vs Profit")
plotly(fig6)

# 7. Sales Distribution Histogram
fig7 = px.histogram(df, x="Sales", nbins=30, title="Sales Distribution")
plotly(fig7)

# 8. Sales Distribution by Segment (Box Plot)
fig8 = px.box(df, x="Segment", y="Sales", title="Sales Distribution by Segment")
plotly(fig8)

# 9. Top 10 Products by Profit Table
top10 = df.groupby("Product Name", as_index=False).agg({"Sales":"sum","Profit":"sum"})
top10 = top10.sort_values("Profit", ascending=False).head(10)
text("### Top 10 Products by Profit")
table(top10)

# Insights
text("## Key Insights")
text("- Furniture category leads in total sales, indicating strong market performance.")
text("- Consumer segment holds the largest share, suggesting Corporate and Home Office are opportunities.")
text("- East region shows robust sales but lower profit margins, pointing to potential cost optimization.")

    # Create segment selector with error handling
    try:
        segment_sel = selectbox(
            "Choose Segment",
            options=["Consumer", "Corporate", "Home Office"],
            default="Consumer",
            key="segment_selector"  # Add a unique key
        )
    except Exception as select_error:
        print(f"Selectbox error: {str(select_error)}")
        segment_sel = "Consumer"  # Fallback to default
        text("⚠️ Error in segment selection, using default: Consumer")

    # Create a fresh copy of filtered data
    try:
        df = df_original[df_original["Segment"] == segment_sel].copy()
    except Exception as filter_error:
        print(f"Filtering error: {str(filter_error)}")
        df = df_original[df_original["Segment"] == "Consumer"].copy()
        text("⚠️ Error in data filtering, showing Consumer segment")

    # 1. Sales vs. Profit by Category
    text("## Sales & Profit by Category")
    cat_stats = df.groupby("Category", as_index=False).agg({
        "Sales": "sum",
        "Profit": "sum"
    }).rename(columns={"Sales": "Total_Sales", "Profit": "Total_Profit"})

    fig1 = px.bar(
        cat_stats,
        x="Category",
        y=["Total_Sales", "Total_Profit"],
        barmode="group",
        title="Sales and Profit by Category",
        labels={"value": "USD", "variable": "Measure"},
        color_discrete_sequence=["#2ecc71", "#3498db"]
    )
    plotly(fig1)

    # 2. Average Profit Margin by Region
    text("## Average Profit Margin by Region")
    region_stats = df.groupby("Region", as_index=False)["Profit Margin"].mean()
    region_stats.columns = ["Region", "Avg_Profit_Margin"]

    fig2 = px.bar(
        region_stats,
        x="Region",
        y="Avg_Profit_Margin",
        title="Average Profit Margin by Region",
        labels={"Avg_Profit_Margin": "Profit Margin"},
        color="Avg_Profit_Margin",
        color_continuous_scale="viridis"
    )
    plotly(fig2)

    # 3. Segment-Specific Profit Margin by Category
    text(f"## Profit Margin by Category: {segment_sel}")
    seg_cat = df.groupby("Category", as_index=False)["Profit Margin"].mean()
    seg_cat.columns = ["Category", "Profit_Margin"]

    fig3 = px.bar(
        seg_cat,
        x="Category",
        y="Profit_Margin",
        title=f"{segment_sel} Segment: Profit Margin by Category",
        labels={"Profit_Margin": "Profit Margin"},
        color_discrete_sequence=["#1abc9c"]
    )
    plotly(fig3)

    # 4. Total Sales by State (USA Map)
    text("## Total Sales by State (USA)")
    state_sales = df.groupby("State_Code", as_index=False)["Sales"].sum()

    fig4 = px.choropleth(
        state_sales,
        locations="State_Code",
        locationmode="USA-states",
        color="Sales",
        scope="usa",
        title="Total Sales by State",
        labels={"Sales": "Total Sales"},
        color_continuous_scale="viridis"
    )
    plotly(fig4)

except Exception as e:
    text(f"Error: {str(e)}")
    print(f"Error: {str(e)}")