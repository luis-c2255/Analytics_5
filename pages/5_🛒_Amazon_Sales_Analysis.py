import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from utils.theme import Components

st.set_page_config(
        page_title=f"Amazon Sales Analysis Analysis",
        page_icon= "🛒",
        layout="wide",
        initial_sidebar_state="expanded"
    )
try:
    with open('style.css') as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
except FileNotFoundError:
    pass

# Load data
@st.cache_data
def load_data():
    df = pd.read_csv('amazon_sales.csv')
    df['order_date'] = pd.to_datetime(df['order_date'])
    df['year'] = df['order_date'].dt.year
    df['month'] = df['order_date'].dt.month
    df['quarter'] = df['order_date'].dt.quarter
    df['year_month'] = df['order_date'].dt.to_period('M').astype(str)
    return df
df = load_data()

st.markdown(
    Components.page_header("🛒 Amazon Sales Analysis Analysis"), unsafe_allow_html=True
)
st.markdown("Comprehensive analysis of 50,000+ orders across categories, regions, and time periods", text_alignment="center")
st.divider()

# Sidebar Filters
st.sidebar.header("🔍 Filters")

# Date range filter
date_range = st.sidebar.date_input(
    "Select Date Range",
    value=(df['order_date'].min(), df['order_date'].max()),
    min_value=df['order_date'].min(),
    max_value=df['order_date'].max()
)
# Category filter
categories = st.sidebar.multiselect(
    "Product Categories",
    options=df['product_category'].unique(),
    default=df['product_category'].unique()
)
# Region filter
regions = st.sidebar.multiselect(
    "Customer Regions",
    options=df['customer_region'].unique(),
    default=df['customer_region'].unique()
)

# Payment method filter
payment_methods = st.sidebar.multiselect(
    "Payment Methods",
    options=df['payment_method'].unique(),
    default=df['payment_method'].unique()
)
# Price range filter
price_range = st.sidebar.slider(
    "Price Range ($)",
    min_value=float(df['price'].min()),
    max_value=float(df['price'].max()),
    value=(float(df['price'].min()), float(df['price'].max()))
)
# Apply filters
filtered_df = df[
    (df['order_date'] >= pd.to_datetime(date_range[0])) &
    (df['order_date'] <= pd.to_datetime(date_range[1])) &
    (df['product_category'].isin(categories)) &
    (df['customer_region'].isin(regions)) &
    (df['payment_method'].isin(payment_methods)) &
    (df['price'] >= price_range[0]) &
    (df['price'] <= price_range[1])
]
st.sidebar.success(f"Showing {len(filtered_df):,} of {len(df):,} orders")

# KPI Metrics
st.subheader("📈 :blue[Key Performance Indicators]", divider="blue")
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    total_revenue = filtered_df['total_revenue'].sum()
    st.markdown(
        Components.metric_card(
            title="Total Revenue",
            value=f"${total_revenue:,.2f}",
            delta="💰",
            card_type="info"
        ), unsafe_allow_html=True
)
with col2:
    total_profit = filtered_df['profit'].sum()
    profit_margin = (total_profit / total_revenue * 100) if total_revenue > 0 else 0
    st.markdown(
        Components.metric_card(
            title="Total Profit",
            value=f"${total_profit:,.2f}",
            delta=f"{profit_margin:.1f}% margin",
            card_type="info"
        ), unsafe_allow_html=True
)
with col3:
    total_orders = len(filtered_df)
    st.markdown(
        Components.metric_card(
            title="Total Orders",
            value=f"{total_orders:,}",
            delta="💲",
            card_type="info"
    ), unsafe_allow_html=True
)
with col4:
    avg_order_value = filtered_df['total_revenue'].mean()
    st.markdown(
        Components.metric_card(
            title="Avg Order Value",
            value=f"${avg_order_value:,.2f}",
            delta="💴",
            card_type="info"
    ), unsafe_allow_html=True
)
with col5:
    avg_rating = filtered_df['rating'].mean()
    st.markdown(
        Components.metric_card(
            title="Avg Rating",
            value=f"{avg_rating:.2f}",
            delta="⭐",
            card_type="info"
    ), unsafe_allow_html=True
)
st.markdown("   ")
st.subheader("📊 :rainbow[Revenue & Profitability by Category]", divider="rainbow")
st.markdown("   ")
# Revenue by Category
category_revenue = filtered_df.groupby('product_category').agg({
    'total_revenue': 'sum',
    'profit': 'sum',
    'order_id': 'count'}).reset_index()
category_revenue.columns = ['Category', 'Revenue', 'Profit', 'Orders']
category_revenue = category_revenue.sort_values('Revenue', ascending=False)
fig1 = px.bar(
    category_revenue,
    x='Category',
    y='Revenue',
    title='Total Revenue by Product Category',
    color='Revenue',
    color_continuous_scale='Blues',
    text_auto='.2s'
)
fig1.update_layout(showlegend=False, xaxis_tickangle=-45)
st.plotly_chart(fig1, width="stretch")
st.markdown("   ")

# Profit by Category
fig2 = px.bar(
    category_revenue,
    x='Category',
    y='Profit',
    title='Total Profit by Product Category',
    color='Profit',
    color_continuous_scale='Greens',
    text_auto='.2s'
)
fig2.update_layout(showlegend=False, xaxis_tickangle=-45)
st.plotly_chart(fig2,  width="stretch")
st.markdown("   ")

# Profit Margin by Category
category_revenue['Profit_Margin'] = (category_revenue['Profit'] / category_revenue['Revenue'] * 100)

fig3 = px.scatter(
    category_revenue,
    x='Revenue',
    y='Profit_Margin',
    size='Orders',
    color='Category',
    title='Profit Margin vs Revenue by Category (Bubble size = Order Count)',
    hover_data=['Orders'],
    text='Category'
)
fig3.update_traces(textposition='top center')
st.plotly_chart(fig3, width="stretch")
st.markdown("   ")

# Data table
st.markdown(":rainbow-background[Category Performance Summary]")
st.dataframe(
    category_revenue.style.format({
        'Revenue': '${:,.2f}',
        'Profit': '${:,.2f}',
        'Profit_Margin': '{:.2f}%'}),
    width="stretch"
)
st.markdown("   ")
st.subheader("💰 :orange[Discount Impact Analysis]", divider="orange")
st.markdown("   ")

# Discount distribution
fig4 = px.histogram(
    filtered_df,
    x='discount_percent',
    nbins=20,
    title='Distribution of Discount Percentages',
    labels={'discount_percent': 'Discount %', 'count': 'Number of Orders'},
    color_discrete_sequence=['#FF6B6B']
)
st.plotly_chart(fig4, width="stretch")
st.markdown("   ")
# Average quantity sold by discount range
discount_bins = [0, 10, 20, 30, 40, 100]
discount_labels = ['0-10%', '10-20%', '20-30%', '30-40%', '40%+']
filtered_df['discount_range'] = pd.cut(
    filtered_df['discount_percent'],
    bins=discount_bins,
    labels=discount_labels
)

discount_impact = filtered_df.groupby('discount_range').agg({
    'quantity_sold': 'mean',
    'total_revenue': 'mean',
    'rating': 'mean'
}).reset_index()

fig5 = px.bar(
    discount_impact,
    x='discount_range',
    y='quantity_sold',
    title='Average Quantity Sold by Discount Range',
    labels={'discount_range': 'Discount Range', 'quantity_sold': 'Avg Quantity'},
    color='quantity_sold',
    color_continuous_scale='Oranges',
    text_auto='.2f'
)
st.plotly_chart(fig5, width="stretch")
st.markdown("   ")
# Discount effectiveness by category
discount_category = filtered_df.groupby(['product_category', 'discount_range']).agg({
    'total_revenue': 'sum',
    'quantity_sold': 'sum'
}).reset_index()

fig6 = px.sunburst(
    discount_category,
    path=['product_category', 'discount_range'],
    values='total_revenue',
    title='Revenue Distribution: Category → Discount Range',
    color='total_revenue',
    color_continuous_scale='RdYlGn'
)
st.plotly_chart(fig6, width="stretch")
st.markdown("   ")

fig7 = px.scatter(
    filtered_df.sample(min(1000, len(filtered_df))), # Sample for performance
    x='discount_percent',
    y='rating',
    color='product_category',
    title='Discount % vs Customer Rating',
    trendline='lowess',
    opacity=0.6
)
st.plotly_chart(fig7, width="stretch")
st.markdown("   ")
# Average revenue per order by discount range
fig8 = px.line(
    discount_impact,
    x='discount_range',
    y='total_revenue',
    title='Average Revenue per Order by Discount Range',
    markers=True,
    line_shape='spline',
    text='total_revenue'
)
fig8.update_traces(texttemplate='$%{text:.2f}', textposition='top center')
st.plotly_chart(fig8, width="stretch")
st.markdown("   ")

st.subheader("🌍 :green[Geographic Performance Analysis]", divider="green")
st.markdown("   ")
# Revenue by region
region_data = filtered_df.groupby('customer_region').agg({
    'total_revenue': 'sum',
    'profit': 'sum',
    'order_id': 'count',
    'rating': 'mean'
}).reset_index()
region_data.columns = ['Region', 'Revenue', 'Profit', 'Orders', 'Avg_Rating']

fig9 = px.pie(
    region_data,
    names='Region',
    values='Revenue',
    title='Revenue Share by Region',
    hole=0.4,
    color_discrete_sequence=px.colors.qualitative.Set3
)
fig9.update_traces(textposition='inside', textinfo='percent+label')
st.plotly_chart(fig9, width="stretch")
st.markdown("   ")

# Orders by region
fig10 = px.bar(
    region_data,
    x='Region',
    y='Orders',
    title='Order Count by Region',
    color='Avg_Rating',
    color_continuous_scale='Viridis',
    text='Orders'
)
fig10.update_traces(texttemplate='%{text:,}', textposition='outside')
st.plotly_chart(fig10, width="stretch")
st.markdown("   ")

# Category preferences by region
region_category = filtered_df.groupby(['customer_region', 'product_category']).agg({
    'total_revenue': 'sum'}).reset_index()

fig11 = px.bar(
    region_category,
    x='customer_region',
    y='total_revenue',
    color='product_category',
    title='Category Preferences by Region',
    barmode='group',
    labels={'total_revenue': 'Total Revenue', 'customer_region': 'Region'}
)
st.plotly_chart(fig11,  width="stretch")
st.markdown("   ")
# Payment method by region
payment_region = filtered_df.groupby(['customer_region', 'payment_method']).size().reset_index(name='count')

fig12 = px.bar(
    payment_region,
    x='customer_region',
    y='count',
    color='payment_method',
    title='Payment Method Preferences by Region',
    barmode='stack',
    labels={'count': 'Number of Orders'}
)
st.plotly_chart(fig12, width="stretch")
st.markdown("   ")
# Regional performance table
st.markdown(":green-background[Regional Performance Summary]")
st.dataframe(region_data.style.format({
    'Revenue': '${:,.2f}',
    'Profit': '${:,.2f}',
    'Orders': '{:,}',
    'Avg_Rating': '{:.2f}'}),width="stretch")
st.markdown("   ")
st.subheader("📅 :blue[Temporal Analysis & Seasonality]", divider="blue")
st.markdown("   ")
# Monthly revenue trend
monthly_data = filtered_df.groupby('year_month').agg({
    'total_revenue': 'sum',
    'profit': 'sum',
    'order_id': 'count'}).reset_index()
monthly_data.columns = ['Month', 'Revenue', 'Profit', 'Orders']

fig13 = make_subplots(specs=[[{"secondary_y": True}]])

fig13.add_trace(
    go.Scatter(
        x=monthly_data['Month'],
        y=monthly_data['Revenue'],
        name='Revenue',
        line=dict(color='#1f77b4', width=3),
        fill='tozeroy'),
secondary_y=False
)

fig13.add_trace(
    go.Scatter(
        x=monthly_data['Month'],
        y=monthly_data['Orders'],
        name='Orders',
        line=dict(color='#ff7f0e', width=2, dash='dot')),
secondary_y=True
)

fig13.update_layout(
    title='Monthly Revenue & Order Trends',
    hovermode='x unified'
)
fig13.update_xaxes(title_text="Month")
fig13.update_yaxes(title_text="Revenue ($)", secondary_y=False)
fig13.update_yaxes(title_text="Number of Orders", secondary_y=True)

st.plotly_chart(fig13, width="stretch")
st.markdown("   ")

# Quarterly performance
quarterly_data = filtered_df.groupby(['year', 'quarter']).agg({
    'total_revenue': 'sum',
    'profit': 'sum'}).reset_index()
quarterly_data['year_quarter'] = quarterly_data['year'].astype(str) + '-Q' + quarterly_data['quarter'].astype(str)

fig14 = px.bar(
    quarterly_data,
    x='year_quarter',
    y=['total_revenue', 'profit'],
    title='Quarterly Revenue vs Profit',
    barmode='group',
    labels={'value': 'Amount ($)', 'variable': 'Metric'}
)
st.plotly_chart(fig14, width="stretch")
st.markdown("   ")

# Day of week analysis
dow_data = filtered_df.groupby('order_date').agg({
    'total_revenue': 'sum',
    'order_id': 'count'}).reset_index()
dow_data['day_of_week'] = dow_data['order_date'].dt.day_name()

day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
dow_summary = dow_data.groupby('day_of_week')['total_revenue'].mean().reindex(day_order).reset_index()

fig15 = px.bar(
    dow_summary,
    x='day_of_week',
    y='total_revenue',
    title='Average Revenue by Day of Week',
    color='total_revenue',
    color_continuous_scale='Sunset'
)
st.plotly_chart(fig15, width="stretch")

# Year-over-year comparison
if filtered_df['year'].nunique() > 1:
    yearly_comparison = filtered_df.groupby(['year', 'month']).agg({
        'total_revenue': 'sum'}).reset_index()

fig16 = px.line(
    yearly_comparison,
    x='month',
    y='total_revenue',
    color='year',
    title='Year-over-Year Monthly Revenue Comparison',
    markers=True,
    labels={'month': 'Month', 'total_revenue': 'Revenue ($)'}
)
fig16.update_xaxes(tickmode='linear', tick0=1, dtick=1)
st.plotly_chart(fig16, width="stretch")
st.markdown("   ")

# Heatmap of sales by month and category
heatmap_data = filtered_df.groupby(['month', 'product_category']).agg({
    'total_revenue': 'sum'}).reset_index()
heatmap_pivot = heatmap_data.pivot(index='product_category', columns='month', values='total_revenue').fillna(0)

fig17 = px.imshow(
    heatmap_pivot,
    title='Revenue Heatmap: Category × Month',
    labels=dict(x="Month", y="Category", color="Revenue"),
    aspect="auto",
    color_continuous_scale='YlOrRd'
)
st.plotly_chart(fig17, width="stretch")
st.markdown("   ")

st.subheader("⭐ :yellow[Customer Ratings & Review Analysis]", divider="yellow")
st.markdown("   ")
# Rating distribution
fig18 = px.histogram(
    filtered_df,
    x='rating',
    nbins=20,
    title='Distribution of Customer Ratings',
    labels={'rating': 'Rating', 'count': 'Number of Orders'},
    color_discrete_sequence=['#9b59b6']
)
fig18.update_layout(bargap=0.1)
st.plotly_chart(fig18, width="stretch")
st.markdown("   ")

# Average rating by category
category_rating = filtered_df.groupby('product_category').agg({
    'rating': 'mean',
    'review_count': 'sum'}).reset_index().sort_values('rating', ascending=False)

fig19 = px.bar(
    category_rating,
    x='product_category',
    y='rating',
    title='Average Rating by Category',
    color='rating',
    color_continuous_scale='RdYlGn',
    range_color=[3, 5],
    text='rating'
)
fig19.update_traces(texttemplate='%{text:.2f}', textposition='outside')
fig19.update_layout(xaxis_tickangle=-45)
st.plotly_chart(fig19, width="stretch")
st.markdown("   ")

# Rating vs Price analysis
# Price bins
filtered_df['price_bin'] = pd.cut(filtered_df['price'], bins=5, precision=0)
price_rating = filtered_df.groupby('price_bin').agg({
    'rating': 'mean',
    'order_id': 'count'}).reset_index()
price_rating['price_bin'] = price_rating['price_bin'].astype(str)

fig20 = px.line(
    price_rating,
    x='price_bin',
    y='rating',
    title='Average Rating by Price Range',
    markers=True,
    text='rating'
)
fig20.update_traces(texttemplate='%{text:.2f}', textposition='top center')
fig20.update_layout(xaxis_tickangle=-45)
st.plotly_chart(fig20, width="stretch")
st.markdown("   ")
# ============================================
# FOOTER
# ============================================
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <p><strong>🛒 Amazon Sales Analysis Analysis</strong></p>
    <p>Explore key metrics, performance, sales & discounts, product, customer feedback and regional analysis.</p>
    <p style='font-size: 0.9rem;'>Navigate using the sidebar to explore different datasets</p>
</div>
""", unsafe_allow_html=True)
