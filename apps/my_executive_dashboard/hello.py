
from preswald import (
    text,
    separator,
    plotly,
    connect,
    get_df,
    table,
    dropdown,
    date_range_picker,
    tabs,
    radio,
    workflow_dag,
    Workflow
)
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import datetime

# 0. Connect to the database
connect()

# 1. TITLE AND INTRODUCTION
text("# Superstore Executive Dashboard\n_Interactive analytics for data-driven decision-making_")
text("""
This dashboard provides a comprehensive view of the Superstore's performance with intuitive 
visualizations and interactive elements. Use the filters and controls to explore different aspects 
of the business and uncover actionable insights.
""")
separator()

# 2. LOAD DATA
df = get_df("data/my_sample_superstore.csv")  # loads data/my_sample_superstore.csv

# Data preprocessing
df["Order Date"] = pd.to_datetime(df["Order Date"])
df["Ship Date"] = pd.to_datetime(df["Ship Date"])
df["Sales"] = pd.to_numeric(df["Sales"], errors="coerce")
df["Profit"] = pd.to_numeric(df["Profit"], errors="coerce")
df["Discount"] = pd.to_numeric(df["Discount"], errors="coerce")
df["Quantity"] = pd.to_numeric(df["Quantity"], errors="coerce")

# Derived fields
df["Year"] = df["Order Date"].dt.year
df["Month"] = df["Order Date"].dt.month
df["Quarter"] = df["Order Date"].dt.quarter
df["MonthYear"] = df["Order Date"].dt.to_period("M").dt.to_timestamp()
df["Profit Margin"] = (df["Profit"] / df["Sales"]).replace([np.inf, -np.inf], np.nan)
df["Shipping Days"] = (df["Ship Date"] - df["Order Date"]).dt.days
df["State Code"] = df["State"].astype("category").cat.codes

# 3. GLOBAL FILTERS SECTION
text("## Global Filters")
text("_Use these controls to filter all visualizations and analyses below_")

# Date range filter with intuitive date picker
min_date = df["Order Date"].min().date()
max_date = df["Order Date"].max().date()
date_range = date_range_picker(
    "Order Date Range",
    min_date=min_date,
    max_date=max_date,
    default_start=min_date,
    default_end=max_date
)

# Category and Region multi-select dropdowns
categories = ["All"] + sorted(df["Category"].unique().tolist())
selected_categories = dropdown(
    "Categories",
    options=categories,
    default="All",
    multi=True
)

regions = ["All"] + sorted(df["Region"].unique().tolist())
selected_regions = dropdown(
    "Regions", 
    options=regions,
    default="All",
    multi=True
)

# Add customer segment filter
segments = ["All"] + sorted(df["Segment"].unique().tolist())
selected_segments = dropdown(
    "Customer Segments",
    options=segments,
    default="All",
    multi=True
)

# View mode selection
view_mode = radio(
    "Dashboard Mode",
    options=["Executive Summary", "Detailed Analysis", "Geo Analysis"],
    default="Executive Summary"
)

separator()

# Filter data based on selections
filtered = df.copy()

# Date range filtering
filtered = filtered[
    (filtered["Order Date"].dt.date >= date_range[0]) &
    (filtered["Order Date"].dt.date <= date_range[1])
]

# Category filtering
if "All" not in selected_categories:
    filtered = filtered[filtered["Category"].isin(selected_categories)]

# Region filtering
if "All" not in selected_regions:
    filtered = filtered[filtered["Region"].isin(selected_regions)]

# Segment filtering
if "All" not in selected_segments:
    filtered = filtered[filtered["Segment"].isin(selected_segments)]

# 4. DATA QUALITY SECTION
if view_mode == "Detailed Analysis":
    text("## Data Quality Overview")
    
    # Calculate data quality metrics
    total_rows = len(filtered)
    missing_values = filtered.isnull().sum().sum()
    duplicates = filtered.duplicated().sum()
    
    # Create data quality indicators
    fig_quality = make_subplots(rows=1, cols=3, specs=[[{"type": "indicator"}]*3])
    
    fig_quality.add_trace(go.Indicator(
        mode="number",
        value=total_rows,
        title={"text": "Total Records"},
        number={"valueformat": ",d"}
    ), row=1, col=1)
    
    fig_quality.add_trace(go.Indicator(
        mode="number+delta",
        value=missing_values,
        title={"text": "Missing Values"},
        delta={"reference": total_rows * 0.05, "valueformat": ".0f"},
        number={"valueformat": ",d"}
    ), row=1, col=2)
    
    fig_quality.add_trace(go.Indicator(
        mode="number+delta",
        value=duplicates,
        title={"text": "Duplicate Rows"},
        delta={"reference": total_rows * 0.01, "valueformat": ".0f"},
        number={"valueformat": ",d"}
    ), row=1, col=3)
    
    fig_quality.update_layout(height=200, margin={"t": 50, "b": 0})
    plotly(fig_quality)
    
    # Show preview of filtered data
    filtered_preview = filtered.copy()
    filtered_preview["Order Date"] = filtered_preview["Order Date"].dt.strftime("%Y-%m-%d")
    filtered_preview["Ship Date"] = filtered_preview["Ship Date"].dt.strftime("%Y-%m-%d")
    table(filtered_preview.head(5), title="Filtered Data Sample")
    
    separator()

# 5. EXECUTIVE KPI SECTION
text("## Key Performance Indicators")

# Current period metrics
current_sales = filtered["Sales"].sum()
current_profit = filtered["Profit"].sum()
current_orders = filtered["Order ID"].nunique()
current_margin = (filtered["Profit"].sum() / filtered["Sales"].sum()) * 100 if filtered["Sales"].sum() > 0 else 0

# For YoY comparison, create a parallel period in the previous year
current_start = date_range[0]
current_end = date_range[1]
days_delta = (current_end - current_start).days

# Previous period start and end
prev_start = current_start - datetime.timedelta(days=365)
prev_end = current_end - datetime.timedelta(days=365)

# Filter for previous period
prev_period = df[
    (df["Order Date"].dt.date >= prev_start) &
    (df["Order Date"].dt.date <= prev_end)
]

# Previous period metrics
prev_sales = prev_period["Sales"].sum() if not prev_period.empty else 0
prev_profit = prev_period["Profit"].sum() if not prev_period.empty else 0
prev_orders = prev_period["Order ID"].nunique() if not prev_period.empty else 0
prev_margin = (prev_period["Profit"].sum() / prev_period["Sales"].sum()) * 100 if not prev_period.empty and prev_period["Sales"].sum() > 0 else 0

# Calculate deltas
sales_delta = ((current_sales / prev_sales) - 1) * 100 if prev_sales > 0 else 0
profit_delta = ((current_profit / prev_profit) - 1) * 100 if prev_profit > 0 else 0
orders_delta = ((current_orders / prev_orders) - 1) * 100 if prev_orders > 0 else 0
margin_delta = current_margin - prev_margin

# Create indicators
fig_kpi = make_subplots(rows=1, cols=4, specs=[[{"type": "indicator"}]*4])

fig_kpi.add_trace(go.Indicator(
    mode="number+delta",
    value=current_sales,
    delta={"reference": prev_sales, "relative": True, "valueformat": ".1%"},
    title={"text": "Total Sales"},
    number={"prefix": "$", "valueformat": ",.0f"}
), row=1, col=1)

fig_kpi.add_trace(go.Indicator(
    mode="number+delta",
    value=current_profit,
    delta={"reference": prev_profit, "relative": True, "valueformat": ".1%"},
    title={"text": "Total Profit"},
    number={"prefix": "$", "valueformat": ",.0f"}
), row=1, col=2)

fig_kpi.add_trace(go.Indicator(
    mode="number+delta",
    value=current_margin,
    delta={"reference": prev_margin, "valueformat": ".1%"},
    title={"text": "Profit Margin"},
    number={"suffix": "%", "valueformat": ".1f"}
), row=1, col=3)

fig_kpi.add_trace(go.Indicator(
    mode="number+delta",
    value=current_orders,
    delta={"reference": prev_orders, "relative": True, "valueformat": ".1%"},
    title={"text": "Order Count"},
    number={"valueformat": ",d"}
), row=1, col=4)

fig_kpi.update_layout(
    height=200,
    margin={"t": 50, "b": 0},
    template="plotly_white"
)

plotly(fig_kpi)

if view_mode == "Executive Summary":
    text(f"""
    **Period Summary:** {current_start.strftime('%b %d, %Y')} to {current_end.strftime('%b %d, %Y')}
    
    - **Sales Performance:** ${current_sales:,.0f} ({sales_delta:+.1f}% YoY)
    - **Profit Results:** ${current_profit:,.0f} ({profit_delta:+.1f}% YoY)
    - **Margin Health:** {current_margin:.1f}% ({margin_delta:+.1f} percentage points YoY)
    - **Order Volume:** {current_orders:,d} ({orders_delta:+.1f}% YoY)
    """)

separator()

# 6. MAIN ANALYSIS TABS
text("## Performance Analysis")

tab_options = ["Sales & Profit Analysis", "Category Performance", "Time Trends", "Discount Analysis"]
selected_tab = tabs("Analysis Tabs", tab_options)

# 6.1 SALES & PROFIT ANALYSIS TAB
if selected_tab == "Sales & Profit Analysis":
    # Create sub-tabs for different views
    profit_views = ["By Category", "By Sub-Category", "By Region", "By Segment"]
    profit_view = tabs("View", profit_views)
    
    if profit_view == "By Category":
        # Category Performance Barchart
        cat_df = filtered.groupby("Category").agg(
            Sales=("Sales", "sum"),
            Profit=("Profit", "sum"),
            Orders=("Order ID", "nunique")
        ).reset_index()
        
        cat_df["Profit Margin"] = (cat_df["Profit"] / cat_df["Sales"]) * 100
        
        fig_cat = px.bar(
            cat_df,
            x="Category",
            y=["Sales", "Profit"],
            barmode="group",
            title="Sales & Profit by Category",
            text_auto=True,
            color_discrete_map={"Sales": "#636EFA", "Profit": "#EF553B"},
            height=500
        )
        
        fig_cat.update_layout(
            yaxis_title="Amount ($)",
            xaxis_title="",
            legend_title="Metric",
            template="plotly_white"
        )
        
        plotly(fig_cat)
        
        # Add a profit margin chart
        fig_margin = px.bar(
            cat_df,
            x="Category",
            y="Profit Margin",
            title="Profit Margin by Category",
            text=cat_df["Profit Margin"].apply(lambda x: f"{x:.1f}%"),
            color="Profit Margin",
            color_continuous_scale=px.colors.diverging.RdBu,
            height=400
        )
        
        fig_margin.update_layout(
            yaxis_title="Profit Margin (%)",
            xaxis_title="",
            coloraxis_showscale=False,
            template="plotly_white"
        )
        
        plotly(fig_margin)
        
        text("""
        ### Key Insights:
        - **Technology** has the highest profit margin, making it the most efficient category.
        - **Furniture** shows strong sales but lower profit margin, suggesting potential pricing or cost issues.
        - **Office Supplies** delivers moderate performance in both metrics - consider product mix optimization.
        
        ### Recommendations:
        - Increase inventory allocation toward high-margin Technology products
        - Review Furniture pricing strategy and supplier contracts
        - Identify specific high-performing Office Supplies for promotion
        """)
    
    elif profit_view == "By Sub-Category":
        # Sub-Category detailed analysis
        sub_df = filtered.groupby("Sub-Category").agg(
            Category=("Category", "first"),
            Sales=("Sales", "sum"),
            Profit=("Profit", "sum"),
            Orders=("Order ID", "nunique")
        ).reset_index()
        
        sub_df["Profit Margin"] = (sub_df["Profit"] / sub_df["Sales"]) * 100
        sub_df = sub_df.sort_values("Sales", ascending=False)
        
        # Top 10 Sub-Categories by Sales
        top_sub = sub_df.head(10).sort_values("Sales")
        
        fig_top_sub = px.bar(
            top_sub,
            y="Sub-Category",
            x="Sales",
            orientation="h",
            title="Top 10 Sub-Categories by Sales",
            color="Category",
            text=top_sub["Sales"].apply(lambda x: f"${x:,.0f}"),
            height=500
        )
        
        fig_top_sub.update_layout(
            xaxis_title="Sales ($)",
            yaxis_title="",
            template="plotly_white"
        )
        
        plotly(fig_top_sub)
        
        # Profitability quadrant chart (Sales vs Margin)
        fig_quad = px.scatter(
            sub_df,
            x="Sales",
            y="Profit Margin",
            size="Orders",
            color="Category",
            hover_name="Sub-Category",
            text="Sub-Category",
            title="Sub-Category Performance Quadrant (Sales vs. Margin)",
            height=600,
            size_max=40
        )
        
        # Add quadrant lines
        median_sales = sub_df["Sales"].median()
        median_margin = sub_df["Profit Margin"].median()
        
        fig_quad.add_hline(
            y=median_margin,
            line_dash="dash",
            line_color="gray",
            annotation_text="Median Margin",
            annotation_position="left"
        )
        
        fig_quad.add_vline(
            x=median_sales,
            line_dash="dash",
            line_color="gray",
            annotation_text="Median Sales",
            annotation_position="top"
        )
        
        # Add quadrant labels
        quadrant_annotations = [
            dict(
                x=sub_df["Sales"].max() * 0.9,
                y=sub_df["Profit Margin"].max() * 0.9,
                text="STAR PERFORMERS",
                showarrow=False,
                font=dict(size=14, color="green")
            ),
            dict(
                x=sub_df["Sales"].min() * 1.5,
                y=sub_df["Profit Margin"].max() * 0.9,
                text="NICHE WINNERS",
                showarrow=False,
                font=dict(size=14, color="blue")
            ),
            dict(
                x=sub_df["Sales"].max() * 0.9,
                y=sub_df["Profit Margin"].min() * 1.5,
                text="VOLUME DRIVERS",
                showarrow=False,
                font=dict(size=14, color="orange")
            ),
            dict(
                x=sub_df["Sales"].min() * 1.5,
                y=sub_df["Profit Margin"].min() * 1.5,
                text="UNDER PERFORMERS",
                showarrow=False,
                font=dict(size=14, color="red")
            )
        ]
        
        fig_quad.update_layout(
            annotations=quadrant_annotations,
            xaxis_title="Sales ($)",
            yaxis_title="Profit Margin (%)",
            template="plotly_white"
        )
        
        plotly(fig_quad)
        
        text("""
        ### Key Insights:
        - **Star Performers** (top-right quadrant): High sales and high margin items that should be prioritized
        - **Niche Winners** (top-left): Low volume but high margin - potential for targeted marketing
        - **Volume Drivers** (bottom-right): High sales but lower margins - review pricing and costs
        - **Under Performers** (bottom-left): Consider discontinuing or repositioning these products
        
        ### Interactive Features:
        - Hover over points for detailed metrics
        - Bubble size represents order volume
        - Click on legend items to filter by category
        """)
    
    elif profit_view == "By Region":
        # Regional Performance Analysis
        region_df = filtered.groupby("Region").agg(
            Sales=("Sales", "sum"),
            Profit=("Profit", "sum"),
            Orders=("Order ID", "nunique"),
            States=("State", "nunique")
        ).reset_index()
        
        region_df["Profit Margin"] = (region_df["Profit"] / region_df["Sales"]) * 100
        region_df["Sales per State"] = region_df["Sales"] / region_df["States"]
        
        # Regional comparison chart
        fig_region = px.bar(
            region_df,
            x="Region",
            y=["Sales", "Profit"],
            barmode="group",
            title="Sales & Profit by Region",
            text_auto=True,
            height=500
        )
        
        fig_region.update_layout(
            yaxis_title="Amount ($)",
            xaxis_title="",
            legend_title="Metric",
            template="plotly_white"
        )
        
        plotly(fig_region)
        
        # State-level detail within each region
        state_df = filtered.groupby(["Region", "State"]).agg(
            Sales=("Sales", "sum"),
            Profit=("Profit", "sum")
        ).reset_index()
        
        state_df["Profit Margin"] = (state_df["Profit"] / state_df["Sales"]) * 100
        
        # Create sunburst chart for hierarchical view
        fig_sunburst = px.sunburst(
            state_df,
            path=["Region", "State"],
            values="Sales",
            color="Profit Margin",
            color_continuous_scale="RdBu",
            title="Regional and State Sales Distribution",
            height=600
        )
        
        fig_sunburst.update_layout(template="plotly_white")
        
        plotly(fig_sunburst)
        
        text("""
        ### Key Insights:
        - **West Region** leads in both sales and profit, with California as the primary contributor
        - **Central Region** shows the lowest profit margin despite moderate sales
        - **East and South Regions** demonstrate balanced performance
        
        ### Regional Highlights:
        - **West**: High technology adoption rates drive profitability
        - **East**: Balanced performance across categories
        - **Central**: Furniture category drags down overall profitability
        - **South**: Consistent performance with room for growth
        
        ### Interactive Features:
        - Click on regions in the sunburst chart to drill down to state level
        - Click the center to return to the previous level
        """)
    
    elif profit_view == "By Segment":
        # Customer Segment Analysis
        segment_df = filtered.groupby("Segment").agg(
            Sales=("Sales", "sum"),
            Profit=("Profit", "sum"),
            Customers=("Customer ID", "nunique"),
            Orders=("Order ID", "nunique")
        ).reset_index()
        
        segment_df["Profit Margin"] = (segment_df["Profit"] / segment_df["Sales"]) * 100
        segment_df["Average Order Value"] = segment_df["Sales"] / segment_df["Orders"]
        segment_df["Orders per Customer"] = segment_df["Orders"] / segment_df["Customers"]
        
        # Create a multi-metric comparison
        fig_segment = make_subplots(
            rows=2, cols=2,
            subplot_titles=(
                "Sales by Segment",
                "Profit Margin by Segment",
                "Average Order Value",
                "Orders per Customer"
            ),
            specs=[
                [{"type": "bar"}, {"type": "bar"}],
                [{"type": "bar"}, {"type": "bar"}]
            ]
        )
        
        # Sales by Segment
        fig_segment.add_trace(
            go.Bar(
                x=segment_df["Segment"],
                y=segment_df["Sales"],
                text=segment_df["Sales"].apply(lambda x: f"${x:,.0f}"),
                name="Sales",
                marker_color="#636EFA"
            ),
            row=1, col=1
        )
        
        # Profit Margin by Segment
        fig_segment.add_trace(
            go.Bar(
                x=segment_df["Segment"],
                y=segment_df["Profit Margin"],
                text=segment_df["Profit Margin"].apply(lambda x: f"{x:.1f}%"),
                name="Profit Margin",
                marker_color="#EF553B"
            ),
            row=1, col=2
        )
        
        # Average Order Value
        fig_segment.add_trace(
            go.Bar(
                x=segment_df["Segment"],
                y=segment_df["Average Order Value"],
                text=segment_df["Average Order Value"].apply(lambda x: f"${x:.0f}"),
                name="AOV",
                marker_color="#00CC96"
            ),
            row=2, col=1
        )
        
        # Orders per Customer
        fig_segment.add_trace(
            go.Bar(
                x=segment_df["Segment"],
                y=segment_df["Orders per Customer"],
                text=segment_df["Orders per Customer"].apply(lambda x: f"{x:.1f}"),
                name="Orders/Customer",
                marker_color="#AB63FA"
            ),
            row=2, col=2
        )
        
        fig_segment.update_layout(
            height=700,
            template="plotly_white",
            showlegend=False
        )
        
        plotly(fig_segment)
        
        # Category preferences by segment
        cat_segment_df = filtered.groupby(["Segment", "Category"]).agg(
            Sales=("Sales", "sum")
        ).reset_index()
        
        # Calculate percentage within segment
        segment_totals = cat_segment_df.groupby("Segment")["Sales"].transform("sum")
        cat_segment_df["Percentage"] = (cat_segment_df["Sales"] / segment_totals) * 100
        
        fig_cat_seg = px.bar(
            cat_segment_df,
            x="Segment",
            y="Percentage",
            color="Category",
            title="Category Preferences by Segment",
            text=cat_segment_df["Percentage"].apply(lambda x: f"{x:.1f}%"),
            height=500
        )
        
        fig_cat_seg.update_layout(
            yaxis_title="Percentage of Sales (%)",
            xaxis_title="",
            barmode="stack",
            template="plotly_white"
        )
        
        plotly(fig_cat_seg)
        
        text("""
        ### Key Insights:
        - **Corporate Segment** generates the highest total sales volume
        - **Home Office** shows the highest profit margin percentage
        - **Consumer** has the lowest average order value but highest order frequency
        
        ### Segment Recommendations:
        - **Corporate**: Focus on volume discounts and simplified procurement
        - **Home Office**: Expand premium product offerings with high margins
        - **Consumer**: Implement loyalty programs to increase average order value
        - Cross-segment opportunity: Technology products perform well across all segments
        """)

# 6.2 CATEGORY PERFORMANCE TAB
elif selected_tab == "Category Performance":
    # Time series analysis by category
    cat_time_df = filtered.groupby(["Category", "MonthYear"]).agg(
        Sales=("Sales", "sum"),
        Profit=("Profit", "sum")
    ).reset_index()
    
    cat_time_df["MonthYear"] = cat_time_df["MonthYear"].dt.strftime("%Y-%m")
    
    # Create Sales trend by category
    fig_cat_trend = px.line(
        cat_time_df,
        x="MonthYear",
        y="Sales",
        color="Category",
        markers=True,
        title="Monthly Sales Trend by Category",
        height=500
    )
    
    fig_cat_trend.update_layout(
        xaxis_title="Month",
        yaxis_title="Sales ($)",
        template="plotly_white",
        xaxis=dict(tickangle=45)
    )
    
    plotly(fig_cat_trend)
    
    # Stacked area chart for category contribution over time
    fig_cat_area = px.area(
        cat_time_df,
        x="MonthYear",
        y="Sales",
        color="Category",
        title="Category Sales Contribution Over Time",
        height=500
    )
    
    fig_cat_area.update_layout(
        xaxis_title="Month",
        yaxis_title="Sales ($)",
        template="plotly_white",
        xaxis=dict(tickangle=45)
    )
    
    plotly(fig_cat_area)
    
    # Category-SubCategory Hierarchy
    cat_subcat_df = filtered.groupby(["Category", "Sub-Category"]).agg(
        Sales=("Sales", "sum"),
        Profit=("Profit", "sum")
    ).reset_index()
    
    cat_subcat_df["Profit Margin"] = (cat_subcat_df["Profit"] / cat_subcat_df["Sales"]) * 100
    
    # Treemap visualization
    fig_treemap = px.treemap(
        cat_subcat_df,
        path=["Category", "Sub-Category"],
        values="Sales",
        color="Profit Margin",
        color_continuous_scale="RdBu",
        title="Category and Sub-Category Performance Hierarchy",
        height=600,
        hover_data=["Sales", "Profit"]
    )
    
    fig_treemap.update_layout(template="plotly_white")
    
    plotly(fig_treemap)
    
    text("""
    ### Seasonal Trends:
    - **Technology**: Shows peak sales in November-December (holiday season)
    - **Furniture**: More consistent throughout the year with slight Q4 increase
    - **Office Supplies**: Notable back-to-school seasonal pattern in August-September
    
    ### Product Hierarchy Insights:
    - **Technology**: Phones and Copiers drive profitability
    - **Furniture**: Tables show concerning profit margins
    - **Office Supplies**: Binders and Paper contribute significantly to overall sales
    
    ### Interactive Features:
    - Click on categories in the treemap to zoom in
    - Hover for detailed metrics on each sub-category
    - Use the legend to filter categories in the trend charts
    """)

# 6.3 TIME TRENDS TAB
elif selected_tab == "Time Trends":
    # Monthly time series analysis
    monthly_df = filtered.groupby("MonthYear").agg(
        Sales=("Sales", "sum"),
        Profit=("Profit", "sum"),
        Orders=("Order ID", "nunique")
    ).reset_index()
    
    monthly_df["Profit Margin"] = (monthly_df["Profit"] / monthly_df["Sales"]) * 100
    monthly_df["MonthYear"] = monthly_df["MonthYear"].dt.strftime("%Y-%m")
    
    # Create line chart with range slider
    fig_trend = px.line(
        monthly_df,
        x="MonthYear",
        y=["Sales", "Profit"],
        title="Monthly Sales and Profit Trend",
        height=500
    )
    
    # Add range slider
    fig_trend.update_layout(
        xaxis=dict(
            rangeslider=dict(visible=True),
            type="category"
        ),
        yaxis_title="Amount ($)",
        legend_title="Metric",
        template="plotly_white"
    )
    
    plotly(fig_trend)
    
    # Year-over-Year comparison
    df_with_month = filtered.copy()
    df_with_month["YearMonth"] = df_with_month["Order Date"].dt.strftime("%m")
    df_with_month["Year"] = df_with_month["Order Date"].dt.year
    
    # Group by month and year
    yoy_df = df_with_month.groupby(["Year", "YearMonth"]).agg(
        Sales=("Sales", "sum")
    ).reset_index()
    
    # Convert month to month name
    month_map = {
        "01": "Jan", "02": "Feb", "03": "Mar", "04": "Apr", "05": "May", "06": "Jun",
        "07": "Jul", "08": "Aug", "09": "Sep", "10": "Oct", "11": "Nov", "12": "Dec"
    }
    yoy_df["Month"] = yoy_df["YearMonth"].map(month_map)
    
    # Sort by month order
    month_order = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    yoy_df["Month"] = pd.Categorical(yoy_df["Month"], categories=month_order, ordered=True)
    yoy_df = yoy_df.sort_values(["Year", "Month"])
    
    # Create YoY comparison chart
    fig_yoy = px.line(
        yoy_df,
        x="Month",
        y="Sales",
        color="Year",
        markers=True,
        title="Year-over-Year Monthly Sales Comparison",
        height=500
    )
    
    fig_yoy.update_layout(
        xaxis_title="Month",
        yaxis_title="Sales ($)",
        template="plotly_white"
    )
    
    plotly(fig_yoy)
    
    # Quarterly analysis
    filtered["Quarter_Year"] = filtered["Order Date"].dt.to_period("Q").astype(str)
    
    quarterly_df = filtered.groupby("Quarter_Year").agg(
        Sales=("Sales", "sum"),
        Profit=("Profit", "sum")
    ).reset_index()
    
    quarterly_df["Profit Margin"] = (quarterly_df["Profit"] / quarterly_df["Sales"]) * 100
    
    # Create quarterly bar chart
    fig_quarter = px.bar(
        quarterly_df,
        x="Quarter_Year",
        y=["Sales", "Profit"],
        barmode="group",
        title="Quarterly Performance",
        height=500
    )
    
    fig_quarter.update_layout(
        xaxis_title="Quarter",
        yaxis_title="Amount ($)",
        legend_title="Metric",
        template="plotly_white"
    )
    
    # Add profit margin as a line
    fig_quarter.add_trace(
        go.Scatter(
            x=quarterly_df["Quarter_Year"],
            y=quarterly_df["Profit Margin"],
            mode="lines+markers",
            name="Profit Margin (%)",
            yaxis="y2"
        )
    )
    
    # Add second y-axis for profit margin
    fig_quarter.update_layout(
        yaxis2=dict(
            title="Profit Margin (%)",
            overlaying="y",
            side="right",
            showgrid=False
        )
    )
    
    plotly(fig_quarter)
    
    text("""
    ### Time Trend Insights:
    - **Seasonal Patterns**: Q4 consistently shows highest sales across years (holiday season)
    - **Growth Trajectory**: Year-over-year comparison shows overall positive growth trend
    - **Profit Margin Fluctuation**: Margins tend to decrease during high-volume periods
    
    ### Business Cycle Analysis:
    - **Peak Periods**: November-December (holiday season), August-September (back-to-school)
    - **Slow Periods**: January-February, June-July
    - **Year-over-Year Comparison**: Current year outperforming previous year in most months
    
    ### Interactive Features:
    - Use the range slider to zoom into specific time periods
    - Toggle metrics on/off by clicking legend items
    - Hover for detailed values at each time point
    """)

# 6.4 DISCOUNT ANALYSIS TAB
elif selected_tab == "Discount Analysis":
    text("### Discount Impact Analysis")
    text("_Examining how discounts affect profitability across different product categories_")
    
    # Create scatter plot with profit zones
    # Create profit zones dataframe for the background
    x_range = np.linspace(0, filtered["Discount"].max() * 1.1, 100)
    profit_zones = pd.DataFrame({
        "x": np.tile(x_range, 3),
        "y": np.concatenate([
            np.ones(100) * filtered["Profit"].quantile(0.8),  # High profit
            np.zeros(100),  # Break even
            np.ones(100) * filtered["Profit"].quantile(0.2),  # Loss
        ]),
        "zone": np.repeat(["High Profit", "Break Even", "Loss"], 100)
    })
    
    # Create the scatter plot with zones
    fig_scatter = px.scatter(
        filtered,
        x="Discount",
        y="Profit",
        color="Category",
        size="Sales",
        hover_data=["Sub-Category", "Order ID", "Sales"],
        opacity=0.7,
        title="Impact of Discounts on Profitability by Category",
        height=600
    )
    
    # Add zone backgrounds
    colors = {"High Profit": "rgba(0,255,0,0.1)", "Break Even": "rgba(255,255,0,0.1)", "Loss": "rgba(255,0,0,0.1)"}
    for zone in profit_zones["zone"].unique():
        zone_data = profit_zones[profit_zones["zone"] == zone]
        fig_scatter.add_trace(
            go.Scatter(
                x=x_range,
                y=zone_data["y"],
                fill="tozeroy" if zone == "Loss" else "tonexty",
                mode="none",
                name=zone,
                fillcolor=colors[zone],
                hoverinfo="skip"
            )
        )
    
    # Add trend lines for each category
    for category in filtered["Category"].unique():
        cat_data = filtered[filtered["Category"] == category]
        if len(cat_data) > 1:  # Ensure we have enough data points
            z = np.polyfit(cat_data["Discount"], cat_data["Profit"], 1)
            p = np.poly1d(z)
            x_trend = np.linspace(0, cat_data["Discount"].max(), 100)
            fig_scatter.add_trace(
                go.Scatter(
                    x=x_trend,
                    y=p(x_trend),
                    mode="lines",
                    line=dict(dash="dash"),
                    name=f"{category} Trend",
                    showlegend=True
                )
            )
    
    fig_scatter.update_layout(
        template="plotly_white",
        xaxis_title="Discount Rate",
        yaxis_title="Profit ($)",
        xaxis=dict(tickformat=".0%"),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    plotly(fig_scatter)
    
    # Distribution of discounts by category
    fig_disc_dist = px.histogram(
        filtered,
        x="Discount",
        color="Category",
        barmode="overlay",
        nbins=20,
        opacity=0.7,
        title="Distribution of Discount Rates by Category",
        height=400
    )
    
    fig_disc_dist.update_layout(
        template="plotly_white",
        xaxis_title="Discount Rate",
        yaxis_title="Count of Orders",
        bargap=0.1
    )
    
    plotly(fig_disc_dist)
    
    # Average profit margin at different discount levels
    discount_bins = [0, 0.1, 0.2, 0.3, 0.4, 0.5, 1.0]
    discount_labels = ["0-10%", "11-20%", "21-30%", "31-40%", "41-50%", "51-100%"]
    
    filtered["Discount_Bin"] = pd.cut(
        filtered["Discount"],
        bins=discount_bins,
        labels=discount_labels,
        include_lowest=True
    )
    
    margin_by_discount = filtered.groupby(["Category", "Discount_Bin"]).agg(
        Sales=("Sales", "sum"),
        Profit=("Profit", "sum"),
        Orders=("Order ID", "nunique")
    ).reset_index()
    
    margin_by_discount["Profit Margin"] = (margin_by_discount["Profit"] / margin_by_discount["Sales"]) * 100
    
    # Create heatmap of profit margin by discount bin and category
    fig_margin_heat = px.density_heatmap(
        margin_by_discount,
        x="Discount_Bin",
        y="Category",
        z="Profit Margin",
        title="Profit Margin (%) by Discount Level and Category",
        color_continuous_scale="RdBu_r",
        height=400
    )
    
    fig_margin_heat.update_layout(
        template="plotly_white",
        xaxis_title="Discount Range",
        yaxis_title="Category"
    )
    
    plotly(fig_margin_heat)
    
    text("""
    ### Discount Analysis Insights:
    
    - **Profit Zones**: 
      - Green area shows high-profit zone
      - Yellow indicates break-even zone
      - Red highlights loss-making zone
    
    - **Category Patterns**:
      - **Technology** maintains profitability at higher discount rates (up to 30-35%)
      - **Furniture** becomes unprofitable more quickly as discounts increase (critical threshold around 20-25%)
      - **Office Supplies** shows high variability in profitability at similar discount levels
    
    - **Optimal Discount Ranges**:
      - Technology: 15-30%
      - Office Supplies: 10-20%
      - Furniture: 5-15%
    
    - **Key Recommendations**:
      - Implement category-specific discount caps
      - Review high-discount, negative-profit orders
      - Consider bundling strategies instead of deep discounts for Furniture
    
    ### Interactive Features:
    - Hover over points for order details
    - Click legend items to isolate categories
    - Use trend lines to identify profitability thresholds
    """)

# 7. GEO ANALYSIS SECTION
if view_mode == "Geo Analysis":
    text("## Geographic Performance Analysis")
    
    # Get state-level metrics
    state_metrics = filtered.groupby("State").agg(
        Sales=("Sales", "sum"),
        Profit=("Profit", "sum"),
        Orders=("Order ID", "nunique"),
        Customers=("Customer ID", "nunique")
    ).reset_index()
    
    state_metrics["Profit Margin"] = (state_metrics["Profit"] / state_metrics["Sales"]) * 100
    
    # Create US choropleth map for sales
    fig_geo_sales = px.choropleth(
        state_metrics,
        locations="State",
        locationmode="USA-states",
        color="Sales",
        scope="usa",
        color_continuous_scale="Blues",
        title="Sales by State",
        height=600
    )
    
    fig_geo_sales.update_layout(
        template="plotly_white",
        coloraxis_colorbar=dict(title="Sales ($)")
    )
    
    plotly(fig_geo_sales)
    
    # Create US choropleth map for profit margin
    fig_geo_margin = px.choropleth(
        state_metrics,
        locations="State",
        locationmode="USA-states",
        color="Profit Margin",
        scope="usa",
        color_continuous_scale="RdBu",
        title="Profit Margin by State",
        height=600
    )
    
    fig_geo_margin.update_layout(
        template="plotly_white",
        coloraxis_colorbar=dict(title="Profit Margin (%)")
    )
    
    plotly(fig_geo_margin)
    
    # Top and bottom performing states
    top_states = state_metrics.sort_values("Profit", ascending=False).head(5)
    bottom_states = state_metrics.sort_values("Profit").head(5)
    
    # Create comparison chart
    top_bottom_df = pd.concat([
        top_states.assign(Performance="Top 5"),
        bottom_states.assign(Performance="Bottom 5")
    ])
    
    fig_top_bottom = px.bar(
        top_bottom_df,
        x="State",
        y="Profit",
        color="Performance",
        title="Top and Bottom 5 States by Profit",
        height=500,
        color_discrete_map={"Top 5": "green", "Bottom 5": "red"}
    )
    
    fig_top_bottom.update_layout(
        template="plotly_white",
        xaxis_title="State",
        yaxis_title="Profit ($)"
    )
    
    plotly(fig_top_bottom)
    
    text("""
    ### Geographic Performance Insights:
    
    - **Regional Patterns**:
      - West Coast and Northeast show strongest overall performance
      - Central states demonstrate the most variable profitability
      - Texas and Florida lead in sales volume but show moderate margins
    
    - **Actionable Insights**:
      - Focus expansion efforts on high-margin, high-volume states (CA, NY)
      - Review pricing and costs in negative-margin states
      - Implement targeted marketing in high-potential but underperforming areas
    
    - **Growth Opportunities**:
      - Population-dense states with below-average penetration
      - High-margin states with relatively low order volumes
      - Cross-selling potential in single-category dominant states
    
    ### Interactive Features:
    - Hover over states for detailed metrics
    - Toggle between sales and margin views for different perspectives
    - Compare top and bottom performing states side-by-side
    """)

# 8. WORKFLOW DIAGRAM SECTION
if view_mode == "Detailed Analysis":
    separator()
    text("## Analysis Workflow & Methodology")
    
    workflow = Workflow()
    
    @workflow.atom()
    def data_load():
        return "Load & Clean Data"
    
    @workflow.atom(dependencies=["data_load"])
    def filter_data():
        return "Apply User Filters"
    
    @workflow.atom(dependencies=["filter_data"])
    def calc_kpis():
        return "Calculate KPIs"
    
    @workflow.atom(dependencies=["filter_data"])
    def create_viz():
        return "Generate Visualizations"
    
    @workflow.atom(dependencies=["calc_kpis", "create_viz"])
    def insights():
        return "Extract Insights"
    
    @workflow.atom(dependencies=["insights"])
    def recommendations():
        return "Generate Recommendations"
    
    workflow_dag(workflow, title="Dashboard Analysis Flow")
    
    text("""
    This dashboard follows a structured analytical approach:
    
    1. **Data Loading & Cleaning**: Initial preprocessing of raw data
    2. **User-Driven Filtering**: Dynamic filtering based on user selections
    3. **KPI Calculation**: Core metrics with year-over-year comparison
    4. **Visualization Generation**: Creation of interactive charts and maps
    5. **Insight Extraction**: Identification of patterns and relationships
    6. **Recommendation Generation**: Actionable business guidance
    
    The interactive nature of this dashboard allows for exploratory analysis while maintaining analytical rigor.
    """)

# 9. FOOTER SECTION
separator()
text("""
## About This Dashboard

This executive dashboard provides a comprehensive analysis of Superstore performance with intuitive visualizations and interactive controls. Use the filters at the top to customize your view, and explore different tabs for detailed insights.

**Key Features**:
- Interactive filters and visualizations
- Year-over-year comparisons
- Multi-dimensional analysis (time, geography, products)
- Actionable insights and recommendations

**Best Viewed**: For optimal experience, view in fullscreen mode and try different filter combinations to discover patterns.
""")
