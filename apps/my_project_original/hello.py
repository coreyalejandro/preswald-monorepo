# hello.py
from preswald import connect, get_df, text, slider, selectbox, plotly, table

import pandas as pd
import plotly.express as px


def main():
    # ─── Init ─────────────────────────────────────────
    connect()
    df = get_df("my_sample_superstore")

    # Preprocess dates and compute profit margin
    df["Order Date"] = pd.to_datetime(df["Order Date"], format="%m/%d/%Y")
    df["Profit Margin"] = df["Profit"] / df["Sales"]

    # ─── Title ───────────────────────────────────────
    text("# 📊 Superstore Sales & Profit Story")

    # ─── Sidebar Controls ───────────────────────────
    min_sales   = slider(
        "Minimum Sales Filter",
        min_val=0,
        max_val=int(df["Sales"].max()),
        default=0
    )
    segment_sel = selectbox(
        "Choose Segment",
        options=sorted(df["Segment"].unique().tolist()),
        default="Consumer"
    )

    # Apply filters
    df = df[(df["Sales"] >= min_sales) & (df["Segment"] == segment_sel)]

    # ─── Section 1: Category Analysis ───────────────
    text("## 1. Sales vs. Profit by Category")
    cat_stats = (
        df.groupby("Category", as_index=False)
          .agg(
            Total_Sales=("Sales", "sum"),
            Total_Profit=("Profit", "sum")
          )
    )
    fig1 = px.bar(
        cat_stats,
        x="Category",
        y=["Total_Sales", "Total_Profit"],
        barmode="group",
        title="Sales and Profit by Category",
        labels={"value":"USD","variable":"Measure"},
        color_discrete_sequence=px.colors.sequential.Teal
    )
    fig1.update_layout(template="plotly_white")
    plotly(fig1)

    # ─── Section 2: Profit Margin by Region ─────────
    text("## 2. Average Profit Margin by Region")
    region_stats = (
        df.groupby("Region", as_index=False)["Profit Margin"]
          .mean()
          .rename(columns={"Profit Margin":"Avg_Profit_Margin"})
    )
    fig2 = px.bar(
        region_stats,
        x="Region",
        y="Avg_Profit_Margin",
        title="Average Profit Margin by Region",
        labels={"Avg_Profit_Margin":"Profit Margin"},
        color="Avg_Profit_Margin",
        color_continuous_scale="Viridis"
    )
    fig2.update_layout(template="plotly_white")
    plotly(fig2)

    # ─── Section 3: Segment → Category Margin ──────
    text(f"## 3. Profit Margin by Category in {segment_sel}")
    seg_cat = (
        df.groupby(["Category"], as_index=False)["Profit Margin"]
          .mean()
          .rename(columns={"Profit Margin":"Profit_Margin"})
    )
    fig3 = px.bar(
        seg_cat,
        x="Category",
        y="Profit_Margin",
        title=f"{segment_sel} Segment: Profit Margin by Category",
        labels={"Profit_Margin":"Profit Margin"},
        color_discrete_sequence=px.colors.sequential.Greens
    )
    fig3.update_layout(template="plotly_white")
    plotly(fig3)

    # ─── Section 4: Sales by State Map ──────────────
    text("## 4. Total Sales by State (USA)")
    state_sales = (
        df.groupby("State", as_index=False)["Sales"]
          .sum()
    )
    fig4 = px.choropleth(
        state_sales,
        locations="State",
        locationmode="USA-states",
        color="Sales",
        title="Total Sales by State",
        scope="usa",
        labels={"Sales":"Total Sales"},
        color_continuous_scale="Cividis"
    )
    fig4.update_layout(template="plotly_white")
    plotly(fig4)
    # ─── Merchandising Visualizations (Codex p14-15) ─────────────────────────
    text("## Merchandising Visualizations (Codex p14-15)")

    # 1. Sales by Category
    cat_sales = df.groupby("Category", as_index=False)["Sales"].sum()
    fig5 = px.bar(cat_sales, x="Category", y="Sales", title="Sales by Category")
    plotly(fig5)

    # 2. Market Share by Segment
    seg_sales = df.groupby("Segment", as_index=False)["Sales"].sum()
    fig6 = px.pie(seg_sales, names="Segment", values="Sales", title="Market Share by Segment")
    plotly(fig6)

    # 3. Trend of Profit Over Time
    profit_trend = df.resample("M", on="Order Date")["Profit"].sum().reset_index()
    fig7 = px.line(profit_trend, x="Order Date", y="Profit", title="Profit Trend Over Time")
    plotly(fig7)

    # 4. Stacked Sales by Region and Category
    reg_cat = df.groupby(["Region", "Category"], as_index=False)["Sales"].sum()
    fig8 = px.bar(reg_cat, x="Region", y="Sales", color="Category", barmode="stack",
                 title="Sales by Region and Category")
    plotly(fig8)

    # 5. Profitability Heatmap: Sub-Category vs Region
    heat_data = df.groupby(["Region", "Sub-Category"], as_index=False)["Profit"].sum()
    heat_pivot = heat_data.pivot(index="Region", columns="Sub-Category", values="Profit").fillna(0)
    fig9 = px.imshow(heat_pivot,
                   labels=dict(x="Sub-Category", y="Region", color="Profit"),
                   title="Profitability by Sub-Category and Region")
    plotly(fig9)

    # 6. Sales vs Profit Scatter
    fig10 = px.scatter(df, x="Sales", y="Profit", title="Sales vs Profit")
    plotly(fig10)

    # 7. Sales Distribution Histogram
    fig11 = px.histogram(df, x="Sales", nbins=30, title="Sales Distribution")
    plotly(fig11)

    # 8. Sales Distribution by Segment (Box Plot)
    fig12 = px.box(df, x="Segment", y="Sales", title="Sales Distribution by Segment")
    plotly(fig12)

    # 9. Top 10 Products by Profit
    top10 = df.groupby("Product Name", as_index=False).agg({"Sales":"sum","Profit":"sum"})
    top10 = top10.sort_values("Profit", ascending=False).head(10)
    text("### Top 10 Products by Profit")
    table(top10)

    # Insights
    text("## Key Insights")
    text("- Furniture category leads in total sales, showing strong performance.")
    text("- Consumer segment holds the largest market share; explore Corporate and Home Office opportunities.")
    text("- East region has high sales but moderate profits, indicating potential pricing issues.")


# Run main
main()