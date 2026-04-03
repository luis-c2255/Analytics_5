import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from utils.theme import Components

st.set_page_config(
        page_title=f"Pypi AI Packages Download Analysis",
        page_icon= "🖥️",
        layout="wide",
        initial_sidebar_state="expanded"
    )
try:
    with open('style.css') as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
except FileNotFoundError:
    pass

@st.cache_data
def load_data():
    df = pd.read_csv('pypi_ai_packages.csv')
    df['date'] = pd.to_datetime(df['date'])
    df['first_release_date'] = pd.to_datetime(df['first_release_date'])
    df['keywords'] = df['keywords'].fillna('not_specified')
    df['license'] = df['license'].fillna('Unknown')
    numeric_cols = ['downloads', 'dependency_count', 'total_versions',
                    'age_days', 'total_downloads', 'avg_daily_downloads',
                    'download_momentum_pct']
    df[numeric_cols] = df[numeric_cols].apply(pd.to_numeric, errors='coerce')
    df['downloads_per_dependency'] = df['downloads'] / (df['dependency_count'] + 1)
    return df
df = load_data()

# Sidebar filters
st.sidebar.title("🎛️ Filters")
date_range = st.sidebar.date_input(
    "Select Date Range",
    value=(df['date'].min(), df['date'].max()),
    min_value=df['date'].min().date(),
    max_value=df['date'].max().date()
)
frameworks = st.sidebar.multiselect(
    "Framework Tags",
    options=df['framework_tag'].unique(),
    default=df['framework_tag'].unique()
)
llm_filter = st.sidebar.radio(
    "Package Era",
    options=['All', 'LLM-Era Only', 'Traditional Only'],
    index=0
)

min_downloads = st.sidebar.slider(
    "Minimum Daily Downloads",
    min_value=0,
    max_value=int(df['downloads'].max()),
    value=0,
    step=1000
)
# Apply filters
mask = (
    (df['date'] >= pd.Timestamp(date_range[0])) &
    (df['date'] <= pd.Timestamp(date_range[1])) &
    (df['framework_tag'].isin(frameworks)) &
    (df['downloads'] >= min_downloads)
)
if llm_filter == 'LLM-Era Only':
    mask &= (df['llm_era_package'] == 'True')
elif llm_filter == 'Traditional Only':
    mask &= (df['llm_era_package'] == 'False')
    
filtered_df = df[mask]

st.markdown(
    Components.page_header("🖥️ Pypi AI Packages Download Analysis"), unsafe_allow_html=True
)
st.markdown(f"Dataset: {len(filtered_df):,} records | Packages: {filtered_df['package_name'].nunique()}", text_alignment="center")

# Key metrics
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown(
        Components.metric_card(
            title="Total Downloads",
            value=f"{filtered_df['downloads'].sum():,.0f}",
            delta="📥",
            card_type="info"
        ), unsafe_allow_html=True
    )
with col2:
    st.markdown(
        Components.metric_card(
            title="Unique Packages",
            value=f"{filtered_df['package_name'].nunique():,}",
            delta="📦",
            card_type="info"
        ), unsafe_allow_html=True
    )
with col3:
    avg_momentum = filtered_df['download_momentum_pct'].mean()
    st.markdown(
        Components.metric_card(
            title="Avg Momentum %",
            value=f"{avg_momentum:.2f}%",
            delta="📨",
            card_type="info"
        ), unsafe_allow_html=True
    )
with col4:
    st.markdown(
        Components.metric_card(
            title="Avg Dependencies",
            value=f"{filtered_df['dependency_count'].mean():.1f}",
            delta="🔁",
            card_type="info"
        ), unsafe_allow_html=True
    )

st.markdown("   ")
st.subheader("📈 :blue[Download Trends Over Time]", divider="blue")
st.markdown("   ")
# Daily downloads trend
daily_downloads = filtered_df.groupby('date')['downloads'].sum().reset_index()
fig_daily = px.line(
    daily_downloads,
    x='date',
    y='downloads',
    title='Daily Total Downloads',
    labels={'downloads': 'Downloads', 'date': 'Date'}
)
fig_daily.update_layout(hovermode='x unified')
st.plotly_chart(fig_daily, width="stretch")
st.markdown("   ")

# Framework trends
framework_daily = filtered_df.groupby(['date', 'framework_tag'])['downloads'].sum().reset_index()
fig_framework = px.line(
    framework_daily,
    x='date',
    y='downloads',
    color='framework_tag',
    title='Downloads by Framework',
    labels={'downloads': 'Downloads', 'date': 'Date'}
)
st.plotly_chart(fig_framework, width="stretch")
st.markdown("   ")
st.markdown(":blue-background[Weekly Download Momentum Heatmap]")
weekly_pivot = filtered_df.groupby(['week', 'package_name'])['download_momentum_pct'].mean().reset_index()
top_packages = filtered_df.groupby('package_name')['total_downloads'].first().nlargest(15).index
weekly_pivot = weekly_pivot[weekly_pivot['package_name'].isin(top_packages)]
pivot_table = weekly_pivot.pivot(index='package_name', columns='week', values='download_momentum_pct')
fig_heatmap = px.imshow(
    pivot_table,
    labels=dict(x="Week", y="Package", color="Momentum %"),
    title="Top 15 Packages - Weekly Momentum",
    color_continuous_scale='RdYlGn',
    aspect='auto'
)
st.plotly_chart(fig_heatmap, width="stretch")
st.markdown("   ")

st.subheader("🏆 :orange[Package Rankings]", divider="orange")
st.markdown("   ")
top_by_downloads = filtered_df.groupby('package_name').agg({
    'total_downloads': 'first',
    'avg_daily_downloads': 'first',
    'download_momentum_pct': 'first'}).nlargest(15, 'total_downloads').reset_index()

fig_top = px.bar(
    top_by_downloads,
    x='total_downloads',
    y='package_name',
    orientation='h',
    title='Top 15 Packages by Total Downloads',
    labels={'total_downloads': 'Total Downloads', 'package_name': 'Package'},
    color='download_momentum_pct',
    color_continuous_scale='Viridis'
)
fig_top.update_layout(yaxis={'categoryorder': 'total ascending'})
st.plotly_chart(fig_top, width="stretch")
st.markdown("   ")

# Fastest growing packages
growth_df = filtered_df.groupby('package_name').agg({
    'download_momentum_pct': 'mean',
    'avg_daily_downloads': 'first'}).reset_index()
growth_df = growth_df[growth_df['avg_daily_downloads'] > 1000] # Filter noise
top_growth = growth_df.nlargest(15, 'download_momentum_pct')

fig_growth = px.bar(
    top_growth,
    x='download_momentum_pct',
    y='package_name',
    orientation='h',
    title='Top 15 Fastest Growing Packages (min 1K daily downloads)',
    labels={'download_momentum_pct': 'Momentum %', 'package_name': 'Package'},
    color='avg_daily_downloads',
    color_continuous_scale='Plasma'
)
fig_growth.update_layout(yaxis={'categoryorder': 'total ascending'})
st.plotly_chart(fig_growth, width="stretch")
st.markdown("   ")

st.markdown(":orange-background[Framework Market Share]")
framework_share = filtered_df.groupby('framework_tag')['downloads'].sum().reset_index()
framework_share = framework_share.sort_values('downloads', ascending=False)
fig_pie = px.pie(
    framework_share,
    values='downloads',
    names='framework_tag',
    title='Downloads Distribution by Framework',
    hole=0.4
)
st.plotly_chart(fig_pie, width="stretch")
st.markdown("   ")

st.subheader("🔍 :violet[Deep Dive Analysis]", divider="violet")
st.markdown("   ")

# Dependency vs Downloads scatter
package_summary = filtered_df.groupby('package_name').agg({
    'dependency_count': 'first',
    'total_downloads': 'first',
    'framework_tag': 'first',
    'llm_era_package': 'first'}).reset_index()

fig_scatter = px.scatter(
    package_summary,
    x='dependency_count',
    y='total_downloads',
    color='framework_tag',
    size='total_downloads',
    hover_data=['package_name'],
    title='Dependencies vs Total Downloads',
    labels={'dependency_count': 'Number of Dependencies', 'total_downloads': 'Total Downloads'},
    log_y=True
)
st.plotly_chart(fig_scatter, width="stretch")
st.markdown("   ")

# Age vs Popularity
age_popularity = filtered_df.groupby('package_name').agg({
    'age_days': 'first',
    'avg_daily_downloads': 'first',
    'llm_era_package': 'first'}).reset_index()

fig_age = px.scatter(
    age_popularity,
    x='age_days',
    y='avg_daily_downloads',
    color='llm_era_package',
    hover_data=['package_name'],
    title='Package Age vs Average Daily Downloads',
    labels={'age_days': 'Age (days)', 'avg_daily_downloads': 'Avg Daily Downloads'},
    log_y=True
)
st.plotly_chart(fig_age, width="stretch")
st.markdown("   ")

st.markdown(":violet-background[LLM-Era vs Traditional Packages]")
comparison_df = filtered_df.groupby('llm_era_package').agg({
    'downloads': 'sum',
    'avg_daily_downloads': 'mean',
    'download_momentum_pct': 'mean',
    'dependency_count': 'mean'}).reset_index()

fig_comparison = make_subplots(
    rows=1, cols=2,
    subplot_titles=('Average Daily Downloads', 'Average Momentum %'),
    specs=[[{'type': 'bar'}, {'type': 'bar'}]]
)

fig_comparison.add_trace(
    go.Bar(
        x=comparison_df['llm_era_package'], 
        y=comparison_df['avg_daily_downloads'],
        name='Avg Daily Downloads', 
        marker_color='indianred'),
        row=1, col=1
)

fig_comparison.add_trace(
    go.Bar(
        x=comparison_df['llm_era_package'], 
        y=comparison_df['download_momentum_pct'],
        name='Momentum %', 
        marker_color='lightsalmon'),
        row=1, col=2
)

fig_comparison.update_layout(showlegend=False, height=400)
st.plotly_chart(fig_comparison, width="stretch")
st.markdown("   ")

st.markdown(":violet-background[Detailed Package Information]")
detailed_table = filtered_df.groupby('package_name').agg({
    'total_downloads': 'first',
    'avg_daily_downloads': 'first',
    'download_momentum_pct': 'first',
    'dependency_count': 'first',
    'age_days': 'first',
    'framework_tag': 'first',
    'license': 'first',
    'author': 'first'}).nlargest(20, 'total_downloads').reset_index()

st.dataframe(
    detailed_table.style.format({
        'total_downloads': '{:,.0f}',
        'avg_daily_downloads': '{:,.0f}',
        'download_momentum_pct': '{:.2f}%',
        'dependency_count': '{:.0f}',
        'age_days': '{:.0f}'}),
    width="stretch", 
    height=400
)

st.subheader("⚖️ :yellow[Ecosystem Health Metrics]", divider="yellow")
st.markdown("   ")
# License distribution
license_dist = filtered_df.groupby('license_group')['downloads'].sum().reset_index()
license_dist = license_dist.sort_values('downloads', ascending=False).head(10)

fig_license = px.bar(
    license_dist,
    x='license_group',
    y='downloads',
    title='Top 10 Licenses by Downloads',
    labels={'license_group': 'License', 'downloads': 'Total Downloads'},
    color='downloads',
    color_continuous_scale='Blues'
)
fig_license.update_layout(xaxis_tickangle=-45)
st.plotly_chart(fig_license, width="stretch")
st.markdown("   ")

# Version maturity distribution
version_bins = filtered_df.groupby('package_name')['total_versions'].first().reset_index()

fig_versions = px.histogram(
    version_bins,
    x='total_versions',
    nbins=30,
    title='Package Version Count Distribution',
    labels={'total_versions': 'Number of Versions', 'count': 'Number of Packages'},
    color_discrete_sequence=['teal']
)
st.plotly_chart(fig_versions, width="stretch")
st.markdown("   ")
st.markdown(":yellow-background[Dependency Complexity]")

dependency_stats = filtered_df.groupby('package_name').agg({
    'dependency_count': 'first',
    'total_downloads': 'first'}).reset_index()

# Create bins for dependency count
dependency_stats['dependency_bin'] = pd.cut(
    dependency_stats['dependency_count'],
    bins=[0, 10, 25, 50, 100, 200],
    labels=['0-10', '11-25', '26-50', '51-100', '100+']
)

dep_analysis = dependency_stats.groupby('dependency_bin').agg({
    'package_name': 'count',
    'total_downloads': 'mean'}).reset_index()
dep_analysis.columns = ['dependency_bin', 'package_count', 'avg_downloads']

fig_dep = make_subplots(
    rows=1, cols=2,
    subplot_titles=('Package Count by Dependency Range', 'Avg Downloads by Dependency Range'),
    specs=[[{'type':'bar'}, {'type': 'bar'}]]
)

fig_dep.add_trace(
    go.Bar(
        x=dep_analysis['dependency_bin'], 
        y=dep_analysis['package_count'],
        name='Package Count', 
        marker_color='steelblue'),
        row=1, col=1
)

fig_dep.add_trace(
    go.Bar(
        x=dep_analysis['dependency_bin'], 
        y=dep_analysis['avg_downloads'],
        name='Avg Downloads', marker_color='coral'),
        row=1, col=2
)

fig_dep.update_xaxes(title_text="Dependency Range", row=1, col=1)
fig_dep.update_xaxes(title_text="Dependency Range", row=1, col=2)
fig_dep.update_yaxes(title_text="Number of Packages", row=1, col=1)
fig_dep.update_yaxes(title_text="Average Downloads", row=1, col=2)
fig_dep.update_layout(showlegend=False, height=400)

st.plotly_chart(fig_dep, width="stretch")
st.markdown("   ")

st.markdown(":yellow-background[Feature Correlation Matrix]")

corr_features = filtered_df.groupby('package_name').agg({
    'dependency_count': 'first',
    'total_versions': 'first',
    'age_days': 'first',
    'avg_daily_downloads': 'first',
    'download_momentum_pct': 'first'
})

corr_matrix = corr_features.corr()

fig_corr = px.imshow(
    corr_matrix,
    text_auto='.2f',
    title='Feature Correlation Heatmap',
    color_continuous_scale='RdBu_r',
    zmin=-1,
    zmax=1,
    aspect='auto'
)
st.plotly_chart(fig_corr, width="stretch")
st.markdown("   ")

st.markdown("📥 :yellow-background[Export Filtered Data]")
csv = filtered_df.to_csv(index=False).encode('utf-8')
st.download_button(
    label="Download Filtered Dataset as CSV",
    data=csv,
    file_name='filtered_pypi_ai_packages.csv',
    mime='text/csv'
)
st.markdown("   ")

with st.expander("📊 Statistical Summary"):
    st.write("Numeric Column Statistics:")
    st.dataframe(filtered_df.describe(), use_container_width=True)

# ============================================
# FOOTER
# ============================================
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <p><strong>🖥️ Pypi AI Packages Download Analysis</strong></p>
    <p>Comprehensive analysis of ecosystem trends, package growth & momentum, licensing and dependencies.</p>
    <p style='font-size: 0.9rem;'>Navigate using the sidebar to explore different datasets</p>
</div>
""", unsafe_allow_html=True)
