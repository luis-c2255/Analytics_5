import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from utils.theme import Components


st.set_page_config(
        page_title=f"Global Volcano Eruption Analysis",
        page_icon= "🌋",
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
    df = pd.read_csv('volcanoes_cleaned.csv')
    df.replace('Unknown', np.nan, inplace=True)
    numeric_cols = [
        "deaths_total", "tsunami_runups", "tsunami_magnitude",
        "tsunami_intensity", "earthquake_magnitude",
        "avg_eruption_return_period_years", "vei", "elevation_m",
        "human_impact_score", "composite_hazard_score", "year"
    ]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    
    bool_cols = [
        'ring_of_fire', 'island_volcano', 'has_casualties',
        'tsunami_confirmed', 'earthquake_confirmed'
    ]
    for col in bool_cols:
        df[col] = df[col].map(
            {True: True, False: False, 'True': True, 'False': False}
        ).astype(bool)
    return df

df = load_data()

# ─────────────────────────────────────────────
# SIDEBAR FILTERS
# ─────────────────────────────────────────────

st.sidebar.image("OIP.svg", width="stretch")
st.markdown("   ")
st.sidebar.title("🌋 Filter Options")

# Era filter
all_eras = sorted(df['era'].dropna().unique().tolist())
selected_eras = st.sidebar.multiselect(
    "Select Era(s)", all_eras, default=all_eras
)

# Continent filter
all_continents = sorted(df['country_continent'].dropna().unique().tolist())
selected_continents = st.sidebar.multiselect(
    "Select Continent(s)", all_continents, default=all_continents
)

# VEI range filter
vei_min, vei_max = int(df['vei'].min()), int(df['vei'].max())
vei_range = st.sidebar.slider(
    "VEI Range", vei_min, vei_max, (vei_min, vei_max)
)

# Ring of Fire filter
rof_filter = st.sidebar.radio(
    "Ring of Fire", ['All', 'Ring of Fire Only', 'Non-Ring of Fire']
)

# Apply filters
filtered = df[
    df["era"].isin(selected_eras) &
    df['country_continent'].isin(selected_continents) &
    df["vei"].between(vei_range[0], vei_range[1])
]
if rof_filter == "Ring of Fire Only":
    filtered = filtered[filtered['ring_of_fire'] == True]
elif rof_filter == "Non-Ring of Fire":
    filtered = filtered[filtered["ring_of_fire"] == False]
    
st.markdown(
    Components.page_header("🌋 Global Volcano Eruption Analysis"), unsafe_allow_html=True
)
st.markdown("Explore 895 eruption events spanning prehistoric times to modern day."
            "Use the sidebar to filter by era, continent, VEI, and tectonic region", text_alignment="center"
        )

# KPI Row
col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    st.markdown(
        Components.metric_card(
            title="Total Eruptions",
            value=f"{len(filtered):,}",
            delta="🌋",
            card_type="info"
        ), unsafe_allow_html=True
    )
with col2:
    st.markdown(
        Components.metric_card(
            title="Unique Volcanoes",
            value=f"{filtered['volcano_name'].nunique():,}",
            delta="🗻",
            card_type="info"
        ), unsafe_allow_html=True
    )
with col3:
    st.markdown(
        Components.metric_card(
            title="Avg VEI",
            value=f"{filtered['vei'].mean():.2f}",
            delta="💥",
            card_type="error"
        ), unsafe_allow_html=True
    )
with col4:
    st.markdown(
        Components.metric_card(
            title="Avg Hazard Score",
            value=f"{filtered['composite_hazard_score'].mean():.1f}",
            delta="⚠️",
            card_type="warning"
        ), unsafe_allow_html=True
    )
with col5:
    st.markdown(
        Components.metric_card(
            title="Casualties",
            value=f"{filtered['has_casualties'].sum():,}",
            delta="☠️",
            card_type="warning"
        ), unsafe_allow_html=True
    )
st.markdown("   ")
st.subheader("🗺️ :green[Geographic Distribution of Eruptions]", divider="green")
st.markdown("   ")
st.markdown(":green-background[Global Eruption Map]")
map_color = st.selectbox(
    "Color points by",
    ['vei', 'composite_hazard_score', 'human_impact_score'],
    key='map_color'
)
map_df = filtered.dropna(subset=['latitude', 'longitude', map_color])
fig_map = px.scatter_geo(
    map_df,
    lat='latitude',
    lon='longitude',
    color=map_color,
    hover_name='volcano_name',
    hover_data={
        'country': True,
        'vei': True,
        'era': True,
        'volcano_type': True,
        'composite_hazard_score': True,
        'latitude': False,
        'longitude': False
    },
    color_continuous_scale="greens",
    size=map_color,
    size_max=18,
    projection='natural earth',
    title=f"Eruptions colored by {map_color.replace('_', ' ').title()}"
)
fig_map.update_layout(
    height=500,
    margin=dict(l=0, r=0, t=40, b=0),
    paper_bgcolor='#0e1117',
    geo=dict(bgcolor='#0e1117', landcolor="#183723", oceancolor="#183a5e")
)
st.plotly_chart(fig_map, width="stretch")
st.markdown("   ")
st.subheader(":green-background[Eruptions by Continent]")

continent_counts = (
    filtered['country_continent'].value_counts().reset_index()
)
continent_counts.columns = ['Continent', 'Count']
fig_cont = px.bar(
    continent_counts,
    x='Count',
    y='Continent',
    orientation='h',    
    color='Count',
    text_auto=True,
    color_continuous_scale="Oranges",
    text='Count'
)
fig_cont.update_traces(textposition='outside')
fig_cont.update_layout(
    height=300,
    showlegend=False,
    coloraxis_showscale=False,
    margin=dict(l=0, r=0, t=10, b=0),
    paper_bgcolor='#0e1117',
    plot_bgcolor='#0e1117',
    font=dict(color='white')
)
st.plotly_chart(fig_cont, width="stretch")
st.markdown("   ")
st.subheader(":green-background[Ring of Fire vs. Non-Ring of Fire]")

rof_counts = filtered['ring_of_fire'].value_counts().reset_index()
rof_counts.columns = ['Ring of Fire', 'Count']
rof_counts['Ring of Fire'] = rof_counts['Ring of Fire'].map(
    {True: 'Ring of Fire', False: 'Non-Ring of Fire'}
)
fig_rof = px.pie(
    rof_counts,
    names='Ring of Fire',
    values='Count',
    color_discrete_sequence=['#ff4b4b', '#4b8bff'],
    hole=0.4
)
fig_rof.update_layout(
    height=250,
    margin=dict(l=0, r=0, t=10, b=0),
    paper_bgcolor='#0e1117',
    font=dict(color='white')
)
st.plotly_chart(fig_rof, width="stretch")
st.markdown("   ")
st.subheader(":green-background[Eruption Count by Country (Top 20)]")

top_countries = (
    filtered['country'].value_counts().head(20).reset_index()
)
top_countries.columns = ['Country', 'Count']
fig_country = px.bar(
    top_countries,
    x='Country',
    y='Count',
    color='Count',
    color_continuous_scale='Reds',
    text='Count'
)
fig_country.update_traces(textposition='outside')
fig_country.update_layout(
    height=400,
    coloraxis_showscale=False,
    margin=dict(l=0, r=0, t=10, b=40),
    paper_bgcolor='#0e1117',
    plot_bgcolor='#0e1117',
    font=dict(color='white'),
    xaxis=dict(tickangle=-35)
)
st.plotly_chart(fig_country, width="stretch")

st.subheader("📈 :yellow[Temporal Patterns]", divider="yellow")
st.markdown("   ")
st.subheader("⚠️ :orange[Hazard & Risk]", divider="orange")
st.markdown("   ")
st.subheader("🌊 :blue[Tsunami & Earthquake Links]", divider="blue")
st.markdown("   ")

# ============================================
# FOOTER
# ============================================
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <p><strong>🌋 Global Volcano Eruption Analysis</strong></p>
    <p>Comprehensive analysis of 898 volcanic eruptions from prehistoric times to present.</p>
    <p style='font-size: 0.9rem;'>Navigate using the sidebar to explore different datasets</p>
</div>
""", unsafe_allow_html=True)
