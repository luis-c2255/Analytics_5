import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime
from utils.theme import Components

st.set_page_config(
        page_title=f"Netflix Content Analysis Analysis",
        page_icon= "📽️",
        layout="wide",
        initial_sidebar_state="expanded"
    )
try:
    with open('style.css') as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
except FileNotFoundError:
    pass


st.markdown(
    Components.page_header("📽️ Netflix Content Analysis Analysis"), unsafe_allow_html=True
)
st.markdown("Comprehensive analysis of Netflix's content library", text_alignment="center")

# Load and prepare data
@st.cache_data
def load_data():
    df = pd.read_csv("netflix_titles.csv")
    df['date_added'] = pd.to_datetime(df['date_added'], errors="coerce")
    df['year_added'] = df["date_added"].dt.year
    df['month_added'] = df['date_added'].dt.month
    df['duration_value'] = df['duration'].str.extract('(\d+)').astype(float)
    df['duration_type'] = df['duration'].str.extract('(min|Season)')
    
    # Handle missing values
    df['director'] = df['director'].fillna('Unknown')
    df['cast'] = df['cast'].fillna('Unknown')
    df['country'] = df['country'].fillna('Unknown')
    df['rating'] = df['rating'].fillna('Not Rated')
    
    # Extract primary values
    df['primary_country'] = df['country'].str.split(',').str[0].str.strip()
    df['primary_genre'] = df['listed_in'].str.split(',').str[0].str.strip()
    
    # Calculate metrics
    df['years_to_netflix'] = df['year_added'] - df['release_year']
    df['content_age'] = datetime.now().year - df['release_year']
    return df
df = load_data()

# Sidebar filters
st.sidebar.title("🎬 Netflix Analytics Filters")
st.sidebar.markdown("---")

# Content type filter
content_types = ['All'] + list(df['type'].unique())
selected_type = st.sidebar.selectbox("Content Type", content_types)

# Year range filter
min_year = int(df['year_added'].min())
max_year = int(df['year_added'].max())
year_range = st.sidebar.slider(
    "Year Added Range",
    min_year, max_year, (min_year, max_year)
)

# Country filter
top_countries = ['All'] + list(df['primary_country'].value_counts().head(20).index)
selected_country = st.sidebar.selectbox("Primary Country", top_countries)

# Rating filter
ratings = ['All'] + list(df['rating'].unique())
selected_rating = st.sidebar.multiselect(
    "Content Rating",
    ratings,
    default=['All']
)

# Apply filters
filtered_df = df.copy()
if selected_type != 'All':
    filtered_df = filtered_df[filtered_df['type'] == selected_type]
    filtered_df = filtered_df[
        (filtered_df['year_added'] >= year_range[0]) &
        (filtered_df['year_added'] <= year_range[1])
    ]
if selected_country != 'All':
    filtered_df = filtered_df[filtered_df['primary_country'] == selected_country]
    
if 'All' not in selected_rating:
    filtered_df = filtered_df[filtered_df['rating'].isin(selected_rating)]
    
# KPI Metrics Row
col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    st.markdown(
        Components.metric_card(
            title="Total Titles",
            value=f"{len(filtered_df):,}",
            delta="",
            card_type="info"
        ), unsafe_allow_html=True
    )
with col2:
    movie_pct = (filtered_df['type'] == 'Movie').sum() / len(filtered_df) * 100
    st.markdown(
        Components.metric_card(
            title="Movies",
            value=f"{movie_pct:.1f}%",
            delta="",
            card_type="info"
        ), unsafe_allow_html=True
    )
with col3:
    tv_pct = (filtered_df['type'] == 'TV Show').sum() / len(filtered_df) * 100
    st.markdown(
        Components.metric_card(
            title="TV Shows",
            value=f"{tv_pct:.1f}%",
            delta="",
            card_type="info"
        ), unsafe_allow_html=True
    )
with col4:
    unique_countries = filtered_df['primary_country'].nunique()
    st.markdown(
        Components.metric_card(
            title="Countries",
            value=f"{unique_countries}",
            delta="",
            card_type="info"
        ), unsafe_allow_html=True
    )
with col5:
    avg_lag = filtered_df[filtered_df['years_to_netflix'] >= 0]['years_to_netflix'].mean()
    st.markdown(
        Components.metric_card(
            title="Avg Years to Netflix",
            value=f"{avg_lag:.1f}",
            delta="",
            card_type="info"
        ), unsafe_allow_html=True
    )
st.markdown("   ")

st.subheader("📈 :blue[Content Trends]", divider="blue")
st.markdown("   ")
st.markdown(":blue-background[Content Addition Trends Over Time]")
st.markdown("   ")
# Yearly content additions by type
yearly_data = filtered_df.groupby(['year_added', 'type']).size().reset_index(name='count')
fig1 = px.line(
    yearly_data,
    x='year_added',
    y='count',
    color='type',
    title='Content Additions by Year and Type',
    labels={'year_added': 'Year', 'count': 'Number of Titles', 'type': 'Content Type'},
    markers=True
)
fig1.update_layout(hovermode='x unified', height=400)
st.plotly_chart(fig1, width="stretch")
st.markdown("   ")
# Monthly seasonality
monthly_data = filtered_df.groupby('month_added').size().reset_index(name='count')
monthly_data['month_name'] = pd.to_datetime(monthly_data['month_added'], format='%m').dt.strftime('%B')
fig2 = px.bar(
    monthly_data,
    x='month_name',
    y='count',
    title='Content Additions by Month (Seasonality)',
    labels={'month_name': 'Month', 'count': 'Number of Titles'},
    color='count',
    color_continuous_scale='Viridis'
)
fig2.update_layout(showlegend=False, height=400)
st.plotly_chart(fig2, width="stretch")
st.markdown("   ")

# Content freshness analysis
st.markdown(":blue-background[Content Freshness: Release Year vs. Addition Year]")
freshness_data = filtered_df[filtered_df['years_to_netflix'] >= 0].copy()
freshness_data['freshness_category'] = pd.cut(
    freshness_data['years_to_netflix'],
    bins=[-1, 0, 2, 5, 10, 100],
    labels=['Same Year', '1-2 Years', '3-5 Years', '6-10 Years', '10+ Years']
)
freshness_counts = freshness_data.groupby(['type', 'freshness_category']).size().reset_index(name='count')

fig3 = px.bar(
    freshness_counts,
    x='freshness_category',
    y='count',
    color='type',
    title='Content Freshness Distribution',
    labels={'freshness_category': 'Time from Release to Netflix', 'count': 'Number of Titles'},
    barmode='group'
)
fig3.update_layout(height=400)
st.plotly_chart(fig3, width="stretch")

st.subheader("🌍 :green[Geographic Analysis]", divider="green")
st.markdown("   ")
country_counts = filtered_df['primary_country'].value_counts().head(15).reset_index()
country_counts.columns = ['country', 'count']

fig4 = px.bar(
    country_counts,
    y='country',
    x='count',
    orientation='h',
    title='Top 15 Content-Producing Countries',
    labels={'country': 'Country', 'count': 'Number of Titles'},
    color='count',
    color_continuous_scale='Blues'
)
fig4.update_layout(showlegend=False, height=500)
st.plotly_chart(fig4, width="stretch")
st.markdown("   ")

# Country content type breakdown (top 10)
top_10_countries = filtered_df['primary_country'].value_counts().head(10).index
country_type_data = filtered_df[filtered_df['primary_country'].isin(top_10_countries)]
country_type_counts = country_type_data.groupby(['primary_country', 'type']).size().reset_index(name='count')

fig5 = px.bar(
    country_type_counts,
    x='primary_country',
    y='count',
    color='type',
    title='Content Type Distribution by Top 10 Countries',
    labels={'primary_country': 'Country', 'count': 'Number of Titles'},
    barmode='stack'
)
fig5.update_layout(xaxis_tickangle=-45, height=500)
st.plotly_chart(fig5, width="stretch")
st.markdown("   ")

# Geographic heatmap
st.markdown(":green-background[Content Production Heatmap by Country and Year]")
# Get top 15 countries for cleaner visualization
top_countries_list = filtered_df['primary_country'].value_counts().head(15).index
heatmap_data = filtered_df[filtered_df['primary_country'].isin(top_countries_list)]
heatmap_pivot = heatmap_data.groupby(['year_added', 'primary_country']).size().reset_index(name='count')
heatmap_pivot = heatmap_pivot.pivot(index='primary_country', columns='year_added', values='count').fillna(0)

fig6 = px.imshow(
    heatmap_pivot,
    labels=dict(x='Year Added', y='Country', color='Number of Titles'),
    title='Content Production Intensity by Country and Year',
    aspect='auto',
    color_continuous_scale='YlOrRd'
)
fig6.update_layout(height=500)
st.plotly_chart(fig6, width="stretch")

st.subheader("🎭 :yellow[Genre & Ratings]", divider="yellow")
st.markdown("   ")
# Top genres
genre_counts = filtered_df['primary_genre'].value_counts().head(15).reset_index()
genre_counts.columns = ['genre', 'count']

fig7 = px.treemap(
    genre_counts,
    path=['genre'],
    values='count',
    title='Top 15 Genres (Treemap)',
    color='count',
    color_continuous_scale='Purples'
)
fig7.update_layout(height=500)
st.plotly_chart(fig7, width="stretch")
st.markdown("   ")

# Content ratings distribution
rating_counts = filtered_df['rating'].value_counts().reset_index()
rating_counts.columns = ['rating', 'count']

fig8 = px.pie(
    rating_counts,
    values='count',
    names='rating',
    title='Content Rating Distribution',
    hole=0.4
)
fig8.update_traces(textposition='inside', textinfo='percent+label')
fig8.update_layout(height=500)
st.plotly_chart(fig8, width="stretch")
st.markdown("   ")

# Genre evolution over time
st.markdown(":yellow-background[Genre Popularity Evolution]")
top_5_genres = filtered_df['primary_genre'].value_counts().head(5).index
genre_time_data = filtered_df[filtered_df['primary_genre'].isin(top_5_genres)]
genre_time_counts = genre_time_data.groupby(['year_added', 'primary_genre']).size().reset_index(name='count')

fig9 = px.area(
    genre_time_counts,
    x='year_added',
    y='count',
    color='primary_genre',
    title='Top 5 Genres: Trends Over Time',
    labels={'year_added': 'Year', 'count': 'Number of Titles', 'primary_genre': 'Genre'}
)
fig9.update_layout(hovermode='x unified', height=400)
st.plotly_chart(fig9, width="stretch")
st.markdown("   ")
# Rating by content type
st.markdown(":yellow-background[Content Rating Distribution by Type]")
rating_type_data = filtered_df.groupby(['rating', 'type']).size().reset_index(name='count')

fig10 = px.bar(
    rating_type_data,
    x='rating',
    y='count',
    color='type',
    title='Rating Distribution: Movies vs TV Shows',
    labels={'rating': 'Content Rating', 'count': 'Number of Titles'},
    barmode='group'
)
fig10.update_layout(xaxis_tickangle=-45, height=400)
st.plotly_chart(fig10, width="stretch")
st.markdown("   ")

st.subheader("⏱️ :red[Duration Analysis]", divider="red")
st.markdown("   ")

# Movies duration analysis
movies_df = filtered_df[filtered_df['type'] == 'Movie'].copy()
tv_shows_df = filtered_df[filtered_df['type'] == 'TV Show'].copy()

if len(movies_df) > 0:
    st.markdown(":red-background[Movie Duration Statistics]")
    fig11 = px.histogram(
        movies_df,
        x='duration_value',
        nbins=50,
        title='Movie Duration Distribution (minutes)',
        labels={'duration_value': 'Duration (minutes)', 'count': 'Frequency'},
        color_discrete_sequence=['#1f77b4']
    )
    fig11.update_layout(showlegend=False, height=400)
    st.plotly_chart(fig11, width="stretch")

duration_stats = movies_df['duration_value'].describe()
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown(
        Components.metric_card(
            title="Avg Duration",
            value=f"{duration_stats['mean']:.0f} min",
            delta="",
            card_type="info"
        ), unsafe_allow_html=True
    )
with col2:
    st.markdown(
        Components.metric_card(
            title="Median Duration",
            value=f"{duration_stats['50%']:.0f} min",
            delta="",
            card_type="info"
        ), unsafe_allow_html=True
    )
with col3:
    st.markdown(
        Components.metric_card(
            title="Std Deviation",
            value=f"{duration_stats['std']:.0f} min",
            delta="",
            card_type="info"
        ), unsafe_allow_html=True
    )
st.markdown("   ")
if len(tv_shows_df) > 0:
    st.markdown(":red-background[TV Show Season Statistics]")
    fig12 = px.histogram(
        tv_shows_df,
        x='duration_value',
        nbins=20,
        title='TV Show Season Count Distribution',
        labels={'duration_value': 'Number of Seasons', 'count': 'Frequency'},
        color_discrete_sequence=['#ff7f0e']
    )
    fig12.update_layout(showlegend=False, height=400)
    st.plotly_chart(fig12, width="stretch")
    
# Summary statistics
season_stats = tv_shows_df['duration_value'].describe()
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown(
        Components.metric_card(
            title="Avg Seasons",
            value=f"{season_stats['mean']:.1f}",
            delta="",
            card_type="info"
        ), unsafe_allow_html=True
    )
with col2:
    st.markdown(
        Components.metric_card(
            title="Median Seasons",
            value=f"{season_stats['50%']:.0f}",
            delta="",
            card_type="info"
        ), unsafe_allow_html=True
    )
with col3:
    st.markdown(
        Components.metric_card(
            title="Max Seasons",
            value=f"{season_stats['max']:.0f}",
            delta="",
            card_type="info"
        ), unsafe_allow_html=True
    )
st.markdown(":red-background[Average Duration Trends Over Time]")
if len(movies_df) > 0:
    movie_duration_trend = movies_df.groupby('year_added')['duration_value'].mean().reset_index()
    movie_duration_trend.columns = ['year_added', 'avg_duration']
    fig13 = px.line(
        movie_duration_trend,
        x='year_added',
        y='avg_duration',
        title='Average Movie Duration by Year',
        labels={'year_added': 'Year Added', 'avg_duration': 'Avg Duration (minutes)'},
        markers=True
    )
    fig13.update_layout(height=350)
    st.plotly_chart(fig13, width="stretch")
if len(tv_shows_df) > 0:
    tv_duration_trend = tv_shows_df.groupby('year_added')['duration_value'].mean().reset_index()
    tv_duration_trend.columns = ['year_added', 'avg_seasons']
    fig14 = px.line(
        tv_duration_trend,
        x='year_added',
        y='avg_seasons',
        title='Average TV Show Seasons by Year',
        labels={'year_added': 'Year Added', 'avg_seasons': 'Avg Number of Seasons'},
        markers=True,
        color_discrete_sequence=['#ff7f0e']
    )
    fig14.update_layout(height=350)
    st.plotly_chart(fig14, width="stretch")

if len(movies_df) > 0:
    st.markdown(":red-background[Movie Duration by Top Genres]")
    top_movie_genres = movies_df['primary_genre'].value_counts().head(10).index
    genre_duration_data = movies_df[movies_df['primary_genre'].isin(top_movie_genres)]
    
    fig15 = px.box(
        genre_duration_data,
        x='primary_genre',
        y='duration_value',
        title='Movie Duration Distribution by Genre (Top 10)',
        labels={'primary_genre': 'Genre', 'duration_value': 'Duration (minutes)'},
        color='primary_genre'
    )
    fig15.update_layout(xaxis_tickangle=-45, showlegend=False, height=450)
    st.plotly_chart(fig15, width="stretch")
    
st.subheader("🎬 :violet[Directors & Cast]", divider="violet")
st.markdown("   ")

st.markdown(":violet-background[Most Prolific Directors]")
directors_df = filtered_df[filtered_df['director'] != 'Unknown'].copy()
# Split directors (some entries have multiple directors)
all_directors = []
for directors in directors_df['director'].dropna():
    all_directors.extend([d.strip() for d in str(directors).split(',')])
    director_counts = pd.Series(all_directors).value_counts().head(15).reset_index()
    director_counts.columns = ['director', 'count']
    fig16 = px.bar(
        director_counts,
        y='director',
        x='count',
        orientation='h',
        title='Top 15 Directors by Number of Titles',
        labels={'director': 'Director', 'count': 'Number of Titles'},
        color='count',
        color_continuous_scale='Reds'
    )
    fig16.update_layout(showlegend=False, height=500)
    st.plotly_chart(fig16, width="stretch")

st.markdown(":violet-background[Director Content Type Preference]")
director_type_data = []
for _, row in directors_df.iterrows():
    if pd.notna(row['director']):
        for director in str(row['director']).split(','):
            director_type_data.append({
                'director': director.strip(),
                'type': row['type']
            })
            director_type_df = pd.DataFrame(director_type_data)
            # Get top 10 directors and their type distribution
            top_10_directors = director_type_df['director'].value_counts().head(10).index
            top_directors_type = director_type_df[director_type_df['director'].isin(top_10_directors)]
            director_type_counts = top_directors_type.groupby(['director', 'type']).size().reset_index(name='count')
            fig17 = px.bar(
                director_type_counts,
                x='director',
                y='count',
                color='type',
                title='Top 10 Directors: Movies vs TV Shows',
                labels={'director': 'Director', 'count': 'Number of Titles'},
                barmode='stack'
            )
            fig17.update_layout(xaxis_tickangle=-45, height=500)
            st.plotly_chart(fig17, width="stretch")
        
st.markdown(":violet-background[Most Featured Cast Members]")
cast_df = filtered_df[filtered_df['cast'] != 'Unknown'].copy()
# Split cast members
all_cast = []
for cast_list in cast_df['cast'].dropna():
    all_cast.extend([c.strip() for c in str(cast_list).split(',')])
    cast_counts = pd.Series(all_cast).value_counts().head(20).reset_index()
    cast_counts.columns = ['actor', 'count']
    
    fig18 = px.bar(
        cast_counts,
        x='actor',
        y='count',
        title='Top 20 Most Featured Actors',
        labels={'actor': 'Actor', 'count': 'Number of Titles'},
        color='count',
        color_continuous_scale='Greens'
    )
    fig18.update_layout(xaxis_tickangle=-45, showlegend=False, height=450)
    st.plotly_chart(fig18, width="stretch")

st.markdown(":violet-background[Top Directors by Primary Genre]")
director_genre_data = []
for _, row in directors_df.head(1000).iterrows(): # Limit for performance
    if pd.notna(row['director']):
        for director in str(row['director']).split(','):
            director_genre_data.append({
                'director': director.strip(),
                'genre': row['primary_genre']
            })

            director_genre_df = pd.DataFrame(director_genre_data)

# Get top 10 directors and their primary genres
top_directors_list = director_genre_df['director'].value_counts().head(10).index
top_directors_genre = director_genre_df[director_genre_df['director'].isin(top_directors_list)]

director_genre_matrix = pd.crosstab(
    top_directors_genre['director'],
    top_directors_genre['genre']
)
fig19 = px.imshow(
    director_genre_matrix,
    labels=dict(x="Genre", y="Director", color="Count"),
    title="Top 10 Directors: Genre Specialization Heatmap",
    aspect="auto",
    color_continuous_scale='Blues'
)
fig19.update_layout(height=500)
st.plotly_chart(fig19, width="stretch")

st.subheader("📊 :rainbow[Key Insights Summary]", divider="rainbow")

col1, col2, col3 = st.columns(3)

with col1:
    recent_growth = filtered_df[filtered_df['year_added'] >= max_year - 2]
    growth_rate = len(recent_growth) / len(filtered_df) * 100 if len(filtered_df) > 0 else 0
    international_pct = (filtered_df['primary_country'] != 'United States').sum() / len(filtered_df) * 100 if len(filtered_df) > 0 else 0
    if len(movies_df) > 0 and len(tv_shows_df) > 0:
        content_ratio = len(movies_df) / len(tv_shows_df)
    with st.expander("Content Strategy"):
        st.markdown("""
            - Recent Content: {growth_rate:.1f}% added in last 2 years.
            - International Content: {international_pct:.1f}% from outside US.
            - Movie to TV Ratio: {content_ratio:.2f}:1
            """)
with col2:
    if len(movies_df) > 0:
        avg_movie_duration = movies_df['duration_value'].mean()
    if len(tv_shows_df) > 0:
        avg_tv_seasons = tv_shows_df['duration_value'].mean()
        top_genre = filtered_df['primary_genre'].value_counts().index[0] if len(filtered_df) > 0 else "N/A"
        with st.expander("Content Characteristics"):
            st.markdown("""
                - Average Movie Length: {avg_movie_duration:.0f} minutes.
                - Most Popular Genre: {top_genre}.
                - Average TV Seasons: {avg_tv_seasons:.1f}.
                """)
with col3:
    top_country = filtered_df['primary_country'].value_counts().index[0] if len(filtered_df) > 0 else "N/A"
    top_country_count = filtered_df['primary_country'].value_counts().values[0] if len(filtered_df) > 0 else 0
    most_common_rating = filtered_df['rating'].value_counts().index[0] if len(filtered_df) > 0 else "N/A"
    unique_directors = filtered_df[filtered_df['director'] != 'Unknown']['director'].nunique()
    with st.expander("Production Insights"):
        st.markdown("""
            - Top Producer: {top_country} ({top_country_count} titles).
            - Most Common Rating: {most_common_rating}.
            - Unique Directors: {unique_directors:,}.
            """)

st.markdown("📥 :rainbow-background[Export Filtered Data]")
csv = filtered_df.to_csv(index=False).encode('utf-8')
st.download_button(
    label="Download Filtered Dataset as CSV",
    data=csv,
    file_name=f'netflix_filtered_{datetime.now().strftime("%Y%m%d")}.csv',
    mime='text/csv',
)



# ============================================
# FOOTER
# ============================================
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <p><strong>📽️ Netflix Content Analysis Analysis</strong></p>
    <p>Comprehensive analysis of Netflix's content library</p>
    <p style='font-size: 0.9rem;'>Navigate using the sidebar to explore different datasets</p>
</div>
""", unsafe_allow_html=True)