import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from utils.theme import Components

st.set_page_config(
        page_title=f"Online Shoppers Purchasing Analysis",
        page_icon= "🛍️",
        layout="wide",
        initial_sidebar_state="expanded"
    )
try:
    with open('style.css') as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
except FileNotFoundError:
    pass


st.markdown(
    Components.page_header("🛍️ Online Shoppers Purchasing Analysis"), unsafe_allow_html=True
)
st.markdown("### Understanding Customer Behavior and Conversion Drivers", text_alignment="center")


@st.cache_data
def load_data():
    df = pd.read_csv("online_shoppers.csv")
    # Clean data
    df['Weekend'] = df['Weekend'].map({'True': True, 'False': False})
    df['Revenue'] = df['Revenue'].map({'True': True, 'False': False})
    
    # Convert Month to ordered categorical
    month_order = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'June',
                   'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    df['Month'] = pd.Categorical(df['Month'], categories=month_order, ordered=True)
    
    return df

df = load_data()

# Sidebar filters
st.sidebar.header("🔍 Filter Data")


# Month filter
selected_months = st.sidebar.multiselect(
    "Select Months",
    options=df['Month'].cat.categories.tolist(),
    default=df['Month'].cat.categories.tolist()
)

# Visitor Type filter
selected_visitors = st.sidebar.multiselect(
    "Select Visitor Type",
    options=df['VisitorType'].unique().tolist(),
    default=df['VisitorType'].unique().tolist()
)

# Weekend filter
weekend_filter = st.sidebar.radio(
    "Weekend/Weekday",
    options=['All', 'Weekday Only', 'Weekend Only']
)
# Apply filters
filtered_df = df[df['Month'].isin(selected_months) &
df['VisitorType'].isin(selected_visitors)]
if weekend_filter == 'Weekday Only':
    filtered_df = filtered_df[filtered_df['Weekend'] == False]
elif weekend_filter == 'Weekend Only':
    filtered_df = filtered_df[filtered_df['Weekend'] == True]
    
col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    total_sessions = len(filtered_df)
    st.markdown(
        Components.metric_card(
            title="Total Sessions",
            value=f"{total_sessions:,}",
            delta="",
            card_type="info"
        ), unsafe_allow_html=True
    )
with col2:
    total_revenue = filtered_df['Revenue'].sum()
    st.markdown(
        Components.metric_card(
            title="Conversions",
            value=f"{total_revenue:,}",
            delta="",
            card_type="info"
        ), unsafe_allow_html=True
    )
with col3:
    conversion_rate = (total_revenue / total_sessions * 100) if total_sessions > 0 else 0
    st.markdown(
        Components.metric_card(
            title="Conversion Rate",
            value=f"{conversion_rate:.2f}%", 
            delta="",
            card_type="info"
        ), unsafe_allow_html=True
    )
with col4:
    avg_page_value = filtered_df['PageValues'].mean()
    st.markdown(
        Components.metric_card(
            title="Avg Page Value",
            value=f"{avg_page_value:.2f}",
            delta="",
            card_type="info"
        ), unsafe_allow_html=True
    )
with col5:
    avg_product_duration = filtered_df['ProductRelated_Duration'].mean()
    st.markdown(
        Components.metric_card(
            title="Avg Product Time (s)",
            value=f"{avg_product_duration:.0f}",
            delta="",
            card_type="info"
        ), unsafe_allow_html=True
    )
    
st.markdown("   ")

st.subheader("📊 :orange[Conversion Overview]", divider="orange")
st.markdown("   ")
# Conversion by Visitor Type
visitor_conv = filtered_df.groupby('VisitorType').agg({
    'Revenue': ['sum', 'count', 'mean']
}).reset_index()
visitor_conv.columns = ['VisitorType', 'Conversions', 'Sessions', 'ConversionRate']
visitor_conv['ConversionRate'] *= 100

fig1 = go.Figure()
fig1.add_trace(go.Bar(
    x=visitor_conv['VisitorType'],
    y=visitor_conv['ConversionRate'],
    text=visitor_conv['ConversionRate'].round(2),
    textposition='auto',
    marker_color=['#FF6B6B', '#4ECDC4', '#45B7D1']
))
fig1.update_layout(
    title="Conversion Rate by Visitor Type",
    xaxis_title="Visitor Type",
    yaxis_title="Conversion Rate (%)",
    height=400
)
st.plotly_chart(fig1, width="stretch")
st.markdown("   ")

# Revenue vs Non-Revenue Distribution
revenue_dist = filtered_df['Revenue'].value_counts()
no_purchase_count = revenue_dist.get(False, 0)
purchase_count = revenue_dist.get(True, 0)

fig2 = go.Figure(data=[go.Pie(
    labels=['No Purchase', 'Purchase'],
    values=[no_purchase_count, purchase_count],
    hole=0.4,
    marker_colors=['#FF6B6B', '#51CF66'],
    textinfo='label+percent',
    textfont_size=14
)])
fig2.update_layout(
    title="Overall Conversion Distribution",
    height=400
)
st.plotly_chart(fig2, width="stretch")
st.markdown("   ")
st.markdown(":orange-background[Session Engagement Funnel]")

total = len(filtered_df)
had_product_pages = len(filtered_df[filtered_df['ProductRelated'] > 0])
had_page_value = len(filtered_df[filtered_df['PageValues'] > 0])
converted = filtered_df['Revenue'].sum()

fig3 = go.Figure(go.Funnel(
    y=['All Sessions', 'Viewed Products', 'High Engagement (PageValue>0)', 'Converted'],
    x=[total, had_product_pages, had_page_value, converted],
    textinfo="value+percent initial",
    marker={"color": ["#667eea", "#764ba2", "#f093fb", "#4facfe"]}
))
fig3.update_layout(height=400)
st.plotly_chart(fig3, width="stretch")
st.markdown("   ")

st.subheader("👥 :violet[Visitor Segmentation]", divider="violet")
st.markdown("   ")

# Average session duration by visitor type and revenue
duration_data = filtered_df.groupby(['VisitorType', 'Revenue']).agg({
    'ProductRelated_Duration': 'mean',
    'Administrative_Duration': 'mean',
    'Informational_Duration': 'mean'
}).reset_index()
duration_data['Revenue'] = duration_data['Revenue'].map({True: 'Converted', False: 'Not Converted'})
duration_data['TotalDuration'] = (duration_data['ProductRelated_Duration'] + duration_data['Administrative_Duration'] + duration_data['Informational_Duration'])

fig4 = px.bar(
    duration_data,
    x='VisitorType',
    y='TotalDuration',
    color='Revenue',
    barmode='group',
    title='Average Session Duration by Visitor Type & Conversion',
    labels={'TotalDuration': 'Duration (seconds)'},
    color_discrete_map={'Converted': '#51CF66', 'Not Converted': '#FF6B6B'}
)
fig4.update_layout(height=400)
st.plotly_chart(fig4, width="stretch")
st.markdown("   ")

filtered_df['Revenue'] = filtered_df['Revenue'].astype('Int64')
# Bounce Rate vs Exit Rate scatter
behavior_data = filtered_df.groupby('VisitorType').agg({
    'BounceRates': 'mean',
    'ExitRates': 'mean',
    'Revenue': 'mean'
}).reset_index()
behavior_data['ConversionRate'] = behavior_data['Revenue'] * 100
behavior_data['ConversionRate'] = behavior_data['ConversionRate'].fillna(0)

fig5 = px.scatter(
    behavior_data,
    x='BounceRates',
    y='ExitRates',
    size='ConversionRate',
    color='VisitorType',
    text='VisitorType',
    title='Bounce Rate vs Exit Rate by Visitor Type',
    labels={'BounceRates': 'Bounce Rate', 'ExitRates': 'Exit Rate'},
    size_max=30
)
fig5.update_traces(textposition='top center')
fig5.update_layout(height=400)
st.plotly_chart(fig5, width="stretch")

st.markdown("   ")
st.markdown(":violet-background[Page Type Engagement Patterns]")
engagement_metrics = filtered_df.groupby('Revenue').agg({
    'Administrative': 'mean',
    'Informational': 'mean',
    'ProductRelated': 'mean'
}).T.reset_index()
engagement_metrics.columns = ['PageType', 'Not Converted', 'Converted']
engagement_metrics = engagement_metrics.melt(id_vars='PageType', var_name='Status', value_name='AvgPages')

fig6 = px.bar(
    engagement_metrics,
    x='PageType',
    y='AvgPages',
    color='Status',
    barmode='group',
    title='Average Pages Viewed by Type and Conversion Status',
    color_discrete_map={'Converted': '#51CF66', 'Not Converted': '#FF6B6B'}
)
fig6.update_layout(height=400)
st.plotly_chart(fig6, width="stretch")
st.markdown("   ")

st.subheader("📅 :yellow[Temporal Patterns & Seasonality]", divider="yellow")
st.markdown("   ")

# Monthly conversion trends
monthly_data = filtered_df.groupby('Month').agg({
    'Revenue': ['sum', 'count', 'mean']
}).reset_index()
monthly_data.columns = ['Month', 'Conversions', 'Sessions', 'ConversionRate']
monthly_data['ConversionRate'] *= 100

fig7 = make_subplots(specs=[[{"secondary_y": True}]])

fig7.add_trace(go.Bar(
    x=monthly_data['Month'],
    y=monthly_data['Sessions'],
    name='Total Sessions',
    marker_color='lightblue'),
    secondary_y=False
)

fig7.add_trace(go.Scatter(
    x=monthly_data['Month'],
    y=monthly_data['ConversionRate'],
    name='Conversion Rate',
    mode='lines+markers',
    line=dict(color='red', width=3),
    marker=dict(size=10)),
    secondary_y=True
)

fig7.update_xaxes(title_text="Month")
fig7.update_yaxes(title_text="Total Sessions", secondary_y=False)
fig7.update_yaxes(title_text="Conversion Rate (%)", secondary_y=True)
fig7.update_layout(title="Monthly Sessions and Conversion Rate Trend", height=400)
st.plotly_chart(fig7, width="stretch")
st.markdown("   ")

# Weekend vs Weekday analysis
weekend_data = filtered_df.groupby('Weekend').agg({
    'Revenue': ['sum', 'count', 'mean']
}).reset_index()
weekend_data.columns = ['Weekend', 'Conversions', 'Sessions', 'ConversionRate']
weekend_data['ConversionRate'] *= 100
weekend_data['DayType'] = weekend_data['Weekend'].map({True: 'Weekend', False: 'Weekday'})

fig8 = go.Figure(
    data=[go.Bar(name='Sessions',
                 x=weekend_data['DayType'],
                 y=weekend_data['Sessions'],
                 marker_color='#667eea'),
          go.Bar(name='Conversions',
                 x=weekend_data['DayType'],
                 y=weekend_data['Conversions'],
                 marker_color='#51CF66')
    ])
fig8.update_layout(title='Weekend vs Weekday Performance', barmode='group', height=400)
st.plotly_chart(fig8, width="stretch")
st.markdown("   ")
# Special day impact
special_day_data = filtered_df.copy()
special_day_data['SpecialDayCategory'] = pd.cut(
    special_day_data['SpecialDay'],
    bins=[-0.1, 0, 0.5, 1.0],
    labels=['No Special Day', 'Near Special Day', 'Special Day']
)

special_conv = special_day_data.groupby('SpecialDayCategory')['Revenue'].agg(['mean', 'count']).reset_index()
special_conv['ConversionRate'] = special_conv['mean'] * 100

fig9 = px.bar(
    special_conv,
    x='SpecialDayCategory',
    y='ConversionRate',
    text='ConversionRate',
    title='Conversion Rate by Special Day Proximity',
    color='ConversionRate',
    color_continuous_scale='Viridis')
fig9.update_traces(texttemplate='%{text:.2f}%', textposition='outside')
fig9.update_layout(height=400, showlegend=False)
st.plotly_chart(fig9, width="stretch")
st.markdown("   ")

st.subheader("🚦 :red[Traffic Source Performance]", divider="red")
st.markdown("   ")

# Top traffic sources
traffic_data = filtered_df.groupby('TrafficType').agg({
    'Revenue': ['sum', 'count', 'mean']
}).reset_index()
traffic_data.columns = ['TrafficType', 'Conversions', 'Sessions', 'ConversionRate']
traffic_data['ConversionRate'] *= 100

# Filter for meaningful traffic (at least 100 sessions)
traffic_data = traffic_data[traffic_data['Sessions'] >= 100].sort_values('ConversionRate', ascending=False)

# Top 15 traffic sources by conversion rate
fig10 = px.bar(
    traffic_data.head(15),
    x='TrafficType',
    y='ConversionRate',
    color='ConversionRate',
    title='Top 15 Traffic Sources by Conversion Rate',
    labels={'TrafficType': 'Traffic Type', 'ConversionRate': 'Conversion Rate (%)'},
    color_continuous_scale='RdYlGn',
    text='ConversionRate')
fig10.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
fig10.update_layout(height=400, showlegend=False)
st.plotly_chart(fig10, width="stretch")
st.markdown("   ")

# Traffic volume vs conversion scatter
fig11 = px.scatter(
    traffic_data,
    x='Sessions',
    y='ConversionRate',
    size='Conversions',
    color='ConversionRate',
    hover_data=['TrafficType'],
    title='Traffic Volume vs Conversion Rate',
    labels={'Sessions': 'Total Sessions', 'ConversionRate': 'Conversion Rate (%)'},
    color_continuous_scale='Viridis')
fig11.update_layout(height=400)
st.plotly_chart(fig11, width="stretch")
st.markdown("   ")

st.markdown(":red-background[Browser & Operating System Analysis]")
browser_data = filtered_df.groupby('Browser').agg({
    'Revenue': ['sum', 'count', 'mean']
}).reset_index()
browser_data.columns = ['Browser', 'Conversions', 'Sessions', 'ConversionRate']
browser_data['ConversionRate'] *= 100
browser_data = browser_data[browser_data['Sessions'] >= 500].sort_values('ConversionRate', ascending=False).head(10)

fig12 = px.bar(
    browser_data,
    y='Browser',
    x='ConversionRate',
    orientation='h',
    title='Top 10 Browsers by Conversion Rate',
    color='ConversionRate',
    color_continuous_scale='Blues',
    text='ConversionRate')
fig12.update_traces(texttemplate='%{text:.2f}%', textposition='outside')
fig12.update_layout(height=400, showlegend=False)
st.plotly_chart(fig12, width="stretch")
st.markdown("   ")

os_data = filtered_df.groupby('OperatingSystems').agg({
    'Revenue': ['sum', 'count', 'mean']
}).reset_index()
os_data.columns = ['OS', 'Conversions', 'Sessions', 'ConversionRate']
os_data['ConversionRate'] *= 100
os_data = os_data[os_data['Sessions'] >= 500].sort_values('ConversionRate', ascending=False).head(10)

fig13 = px.bar(
    os_data,
    y='OS',
    x='ConversionRate',
    orientation='h',
    title='Top 10 Operating Systems by Conversion Rate',
    color='ConversionRate',
    color_continuous_scale='Greens',
    text='ConversionRate')
fig13.update_traces(texttemplate='%{text:.2f}%', textposition='outside')
fig13.update_layout(height=400, showlegend=False)
st.plotly_chart(fig13, width="stretch")
st.markdown("   ")

st.subheader("💎 :blue[Behavioral Insights & Feature Importance]", divider="blue")
st.markdown("   ")
st.markdown(":blue-background[Page Value Impact on Conversion]")

# PageValue distribution for converters vs non-converters
pagevalue_conv = filtered_df[filtered_df['Revenue'] == True]['PageValues']
pagevalue_noconv = filtered_df[filtered_df['Revenue'] == False]['PageValues']

fig14 = go.Figure()
fig14.add_trace(
    go.Histogram(x=pagevalue_conv[pagevalue_conv > 0],
                 name='Converted',
                 marker_color='#51CF66',
                 opacity=0.7,
                 nbinsx=50))
fig14.add_trace(
    go.Histogram(x=pagevalue_noconv[pagevalue_noconv > 0],
                 name='Not Converted',
                 marker_color='#FF6B6B',
                 opacity=0.7,
                 nbinsx=50))
fig14.update_layout(
    title='Page Value Distribution (PageValue > 0)',
    xaxis_title='Page Value',
    yaxis_title='Frequency',
    barmode='overlay',
    height=400
)
st.plotly_chart(fig14, width="stretch")
st.markdown("   ")

# Create PageValue categories
pv_data = filtered_df.copy()
pv_data['PageValueCategory'] = pd.cut(
    pv_data['PageValues'],
    bins=[-0.1, 0, 10, 50, 100, 1000],
    labels=['Zero', 'Low (0-10)', 'Medium (10-50)', 'High (50-100)', 'Very High (100+)']
)

pv_conv = pv_data.groupby('PageValueCategory')['Revenue'].agg(['mean', 'count']).reset_index()
pv_conv['ConversionRate'] = pv_conv['mean'] * 100

fig15 = px.line(
    pv_conv,
    x='PageValueCategory',
    y='ConversionRate',
    markers=True,
    title='Conversion Rate by Page Value Category',
    labels={'ConversionRate': 'Conversion Rate (%)', 'PageValueCategory': 'Page Value Range'})
fig15.update_traces(line=dict(width=3, color='#667eea'), marker=dict(size=12))
fig15.update_layout(height=400)
st.plotly_chart(fig15, width="stretch")
st.markdown("   ")

# Bounce and Exit Rate Analysis
st.markdown(":blue-background[Bounce & Exit Rate Impact]")
st.markdown("   ")
# Average bounce and exit rates
bounce_exit = filtered_df.groupby('Revenue').agg({
    'BounceRates': 'mean',
    'ExitRates': 'mean'
}).reset_index()
bounce_exit['Revenue'] = bounce_exit['Revenue'].map({True: 'Converted', False: 'Not Converted'})
bounce_exit_melted = bounce_exit.melt(id_vars='Revenue', var_name='Metric', value_name='Rate')

fig16 = px.bar(
    bounce_exit_melted,
    x='Revenue',
    y='Rate',
    color='Metric',
    barmode='group',
    title='Average Bounce & Exit Rates by Conversion Status',
    labels={'Rate': 'Rate (average)', 'Revenue': 'Conversion Status'},
    color_discrete_map={'BounceRates': '#FF6B6B', 'ExitRates': '#FFA94D'})
fig16.update_layout(height=400)
st.plotly_chart(fig16, width="stretch")
st.markdown("   ")

# Product-related pages and duration impact
product_data = filtered_df.groupby('Revenue').agg({
    'ProductRelated': 'mean',
    'ProductRelated_Duration': 'mean'
}).reset_index()
product_data['Revenue'] = product_data['Revenue'].map({True: 'Converted', False: 'Not Converted'})

fig17 = make_subplots(specs=[[{"secondary_y": True}]])

fig17.add_trace(
    go.Bar(x=product_data['Revenue'],
           y=product_data['ProductRelated'],
           name='Avg Product Pages',
           marker_color='#4ECDC4'),
    secondary_y=False
)

fig17.add_trace(
    go.Scatter(x=product_data['Revenue'],
               y=product_data['ProductRelated_Duration'],
               name='Avg Duration (s)',
               mode='lines+markers',
               line=dict(color='#FF6B6B', width=3),
               marker=dict(size=12)), secondary_y=True
)

fig17.update_xaxes(title_text="Conversion Status")
fig17.update_yaxes(title_text="Avg Product Pages", secondary_y=False)
fig17.update_yaxes(title_text="Avg Duration (seconds)", secondary_y=True)
fig17.update_layout(title="Product Engagement by Conversion Status", height=400)
st.plotly_chart(fig17, width="stretch")
st.markdown("   ")
st.markdown(":blue-background[Key Behavioral Metrics Comparison]")
st.markdown("   ")

metrics_comparison = filtered_df.groupby('Revenue').agg({
    'Administrative': 'mean',
    'Administrative_Duration': 'mean',
    'Informational': 'mean',
    'Informational_Duration': 'mean',
    'ProductRelated': 'mean',
    'ProductRelated_Duration': 'mean',
    'BounceRates': 'mean',
    'ExitRates': 'mean',
    'PageValues': 'mean'
}).T.reset_index()
metrics_comparison.columns = ['Metric', 'Not Converted', 'Converted']
metrics_comparison['Difference'] = metrics_comparison['Converted'] - metrics_comparison['Not Converted']
metrics_comparison['PercentChange'] = (metrics_comparison['Difference'] / metrics_comparison['Not Converted'] * 100).round(2)

# Show table
st.dataframe(
    metrics_comparison.style.background_gradient(
        subset=['PercentChange'], cmap='RdYlGn', vmin=-50, vmax=50), 
        width="stretch",
        height=400
)
# ============================================
# FOOTER
# ============================================
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <p><strong>🛍️ Online Shoppers Purchasing Analysis</strong></p>
    <p>Explore key metrics, understand Customer Behavior and Conversion Drivers.</p>
    <p style='font-size: 0.9rem;'>Navigate using the sidebar to explore different datasets</p>
</div>
""", unsafe_allow_html=True)