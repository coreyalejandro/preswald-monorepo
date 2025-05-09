import pandas as pd
import plotly.express as px
from preswald import connect, text, sidebar, plotly, table

# 1) Start the Preswald server connection
connect()
# 2) Build your sidebar
sidebar()
text("# Superstore Saga")
text("## A Data Visualization Documentary")

# 3) Load the data directly (matches your preswald.toml data key)
df = pd.read_csv("data/my_sample_superstore.csv")
df["Sales"] = pd.to_numeric(df["Sales"], errors="coerce")

# Convert all datetime columns to string to avoid serialization issues
for col in df.columns:
    if df[col].dtype == 'datetime64[ns]':
        df[col] = df[col].astype(str)
    # Consider other object types that might cause issues, if necessary
    # For example, to convert all 'object' columns that might be dates but not parsed as datetime64
    # elif df[col].dtype == 'object':
    #     try:
    #         df[col] = pd.to_datetime(df[col]).astype(str)
    #     except (ValueError, TypeError):
    #         pass # Not a convertible date string

# 4) Give a quick status message
text(f"Loaded {len(df)} records")

# 5) Render a simple sales‐histogram
fig = px.histogram(df, x="Sales", nbins=30, title="Sales Distribution")
fig.update_layout(template="plotly_white")
plotly(fig)
# 6) Render the raw data as a table
table(df)