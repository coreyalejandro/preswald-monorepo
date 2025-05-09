from preswald import text, plotly, connect, get_df, table
import plotly.express as px
# matplotlib and seaborn imports not used

# Initialize connection and data
connect()
df = get_df("my_sample_superstore")

def analyze_sales():
    # Display total sales and profit
    total_sales = df['Sales'].sum()
    total_profit = df['Profit'].sum()
    text(f"Total Sales: ${total_sales:,.2f}")
    text(f"Total Profit: ${total_profit:,.2f}")
    
    # Create a sales by category plot
    sales_by_category = df.groupby('Category')['Sales'].sum().reset_index()
    fig = px.bar(
        sales_by_category,
        x='Category',
        y='Sales',
        title='Sales by Category',
    )
    plotly(fig)
    
    # Show top 10 products by profit
    top_products = df.groupby('Product Name')[['Sales', 'Profit']].sum().sort_values('Profit', ascending=False).head(10)
    table(top_products, title='Top 10 Products by Profit')

def main():
    text("# Superstore Sales Analysis")
    analyze_sales()
    table(df, title='Full Dataset')

# Run main
main()

# Make data and functions available in REPL

__all__ = ['df', 'analyze_sales', 'main']