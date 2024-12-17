import pandas as pd
import streamlit as st
import glob
import os
import pickle
# ---- File Path ----

# ---- Function to Merge Monthly Reports import from pickle ----
with open('df.pickle', 'rb') as f:
    data = pickle.load(f)
df=data
# ---- Load and Clean Dataset ----
#df = merge_monthly_reports(folder_path)
df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
df['Total'] = pd.to_numeric(df['Total'], errors='coerce')
df['Qty'] = pd.to_numeric(df['Qty'], errors='coerce')
df['Year-Month'] = df['Date'].dt.strftime('%Y-%m')

# ---- Streamlit App ----
st.title("Sales Dashboard")

# ---- Filters ----
# Create a dropdown filter for Year-Month
month_options = ['All'] + df['Year-Month'].sort_values(ascending=False).unique().tolist()
selected_month = st.selectbox("Select a Month", month_options)

# Create a multiselect filter for Channel Ledger
channel_options = ['All'] + df['Channel Ledger'].dropna().unique().tolist()
selected_channels = st.multiselect("Select Channels", channel_options, default='All')

# ---- Apply Filters ----
filtered_df = df.copy()

# Filter by selected month
if selected_month != 'All':
    filtered_df = filtered_df[filtered_df['Year-Month'] == selected_month]

# Filter by selected channels
if 'All' not in selected_channels:
    filtered_df = filtered_df[filtered_df['Channel Ledger'].isin(selected_channels)]

# ---- Revenue Summary ----
st.header("Revenue Summary")
total_revenue = filtered_df['Total'].sum()
aov = total_revenue / filtered_df['Qty'].sum() if filtered_df['Qty'].sum() > 0 else 0
total_orders = filtered_df['Qty'].sum()

col1, col2, col3 = st.columns(3)
col1.metric("Total Revenue", f"₹{total_revenue:,.2f}")
col2.metric("Average Order Value (AOV)", f"₹{aov:,.2f}")
col3.metric("Total Orders", total_orders)

# ---- Revenue by Channel ----
st.subheader("Revenue by Channel")
revenue_by_channel = filtered_df.groupby('Channel Ledger')['Total'].sum().reset_index()
st.bar_chart(revenue_by_channel.set_index('Channel Ledger'))

# ---- Top Products ----
st.subheader("Top Products by Quantity Sold")
top_products_qty = filtered_df.groupby('Product Name')['Qty'].sum().sort_values(ascending=False).head(10)
st.table(top_products_qty)

st.subheader("Top Products by Revenue")
top_products_revenue = filtered_df.groupby('Product Name')['Total'].sum().sort_values(ascending=False).head(10)
st.table(top_products_revenue)

# ---- Geographical Insights ----
st.subheader("Revenue by State")
revenue_by_state = filtered_df.groupby('Shipping Address State')['Total'].sum().sort_values(ascending=False).head(10)
st.bar_chart(revenue_by_state)

# ---- Tax Analysis ----
st.subheader("Tax Analysis")
total_cgst = filtered_df['CGST'].sum()
total_sgst = filtered_df['SGST'].sum()
total_igst = filtered_df['IGST'].sum()
st.write(f"Total CGST Collected: ₹{total_cgst:,.2f}")
st.write(f"Total SGST Collected: ₹{total_sgst:,.2f}")
st.write(f"Total IGST Collected: ₹{total_igst:,.2f}")

# ---- Month-on-Month Revenue Analysis ----
st.subheader("Month-on-Month Revenue")
monthly_revenue = filtered_df.groupby('Year-Month')['Total'].sum().reset_index()
monthly_revenue['MoM Change'] = monthly_revenue['Total'].pct_change() * 100
st.line_chart(monthly_revenue.set_index('Year-Month')['MoM Change'])
