import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.cluster import KMeans
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, r2_score
import warnings
warnings.filterwarnings("ignore")
from utils.theme import Components

st.set_page_config(
        page_title=f"Mental Health Burnout Analysis",
        page_icon= "🤯",
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
    df = pd.read_csv("tech_mental_health_burnout.csv")
    df = df.drop_duplicates()
    numeric_cols = df.select_dtypes(include=np.number).columns
    df[numeric_cols] = df[numeric_cols].fillna(df[numeric_cols].median())
    cat_cols = df.select_dtypes(include="object").columns
    for col in cat_cols:
        df[col] = df[col].fillna(df[col].mode()[0])
        df[col] = df[col].str.strip().str.title()
    return df
df = load_data()

st.sidebar.image("https://img.icons8.com/fluency/96/brain.png", width=60)
st.sidebar.title("🔍 Filters")
work_modes = ["All"] + sorted(df["work_mode"].unique().tolist())
selected_work_mode = st.sidebar.selectbox("Work Mode", work_modes)

company_sizes = ["All"] + sorted(df["company_size"].unique().tolist())
selected_company_size = st.sidebar.selectbox("Company Size", company_sizes)

job_roles = ["All"] + sorted(df["job_role"].unique().tolist())
selected_job_role = st.sidebar.selectbox("Job Role", job_roles)

genders = ["All"] + sorted(df["gender"].unique().tolist())
selected_gender = st.sidebar.selectbox("Gender", genders)

age_min, age_max = int(df["age"].min()), int(df["age"].max())
selected_age = st.sidebar.slider("Age Range", age_min, age_max, (age_min, age_max))

burnout_levels = ["All"] + sorted(df["burnout_level"].unique().tolist())
selected_burnout = st.sidebar.selectbox("Burnout Level", burnout_levels)

st.sidebar.markdown("   ")
st.sidebar.markdown(f"Records after filters:")
# Apply filters
filtered = df.copy()
if selected_work_mode != "All":
    filtered = filtered[filtered["work_mode"] == selected_work_mode]
if selected_company_size != "All":
    filtered = filtered[filtered["company_size"] == selected_company_size]
if selected_job_role != "All":
    filtered = filtered[filtered["job_role"] == selected_job_role]
if selected_gender != "All":
    filtered = filtered[filtered["gender"] == selected_gender]
if selected_burnout != "All":
    filtered = filtered[filtered["burnout_level"] == selected_burnout]
    filtered = filtered[filtered["age"].between(selected_age[0], selected_age[1])]

st.sidebar.markdown(f"### 🟢 {len(filtered):,}")

st.markdown(
    Components.page_header("🤯 Mental Health Burnout Analysis"), unsafe_allow_html=True
)
st.markdown("### Analyzing 150,000 tech professionals across work habits, lifestyle, and mental health indicators.", text_alignment="center")
st.markdown("   ")

# ─────────────────────────────────────────────
# KPI METRICS ROW
# ─────────────────────────────────────────────
col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    avg_burnout = filtered["burnout_score"].mean()
    st.markdown(
        Components.metric_card(
            title="Avg Burnout Score",
            value=f"{avg_burnout:.2f}",
            delta="🔥",
            card_type="info"
        ), unsafe_allow_html=True
    )
with col2:
    avg_stress = filtered["stress_level"].mean()
    st.markdown(
        Components.metric_card(
            title="Avg Stress Level",
            value=f"{avg_stress:.2f}",
            delta="😰",
            card_type="info"
        ), unsafe_allow_html=True
    )
with col3:
    avg_sleep = filtered["sleep_hours"].mean()
    st.markdown(
        Components.metric_card(
            title="Avg Sleep Hours",
            value=f"{avg_sleep:.1f}h",
            delta="😴",
            card_type="info"
        ), unsafe_allow_html=True
    )
with col4:
    pct_therapy = filtered["has_therapy"].mean() * 100
    st.markdown(
        Components.metric_card(
            title="In Therapy",
            value=f"{pct_therapy:.1f}%",
            delta="🧘",
            card_type="info"
        ), unsafe_allow_html=True
    )
with col5:
    pct_seeks_help = filtered["seeks_professional_help"].mean() * 100
    st.markdown(
        Components.metric_card(
            title="Seeks Help",
            value=f"{pct_seeks_help:.1f}%",
            delta="🆘",
            card_type="info"
        ), unsafe_allow_html=True
    )
st.markdown("   ")

st.subheader("📊 :rainbow[Burnout & Mental Health Overview]", divider="rainbow")
st.markdown("   ")
st.markdown(":rainbow-background[Burnout Level Distribution]")

burnout_counts = filtered["burnout_level"].value_counts().reset_index()
burnout_counts.columns = ["burnout_level", "count"]
color_map = {"Low": "#2ecc71", "Moderate": "#f39c12", "High": "#e74c3c"}
fig = px.pie(
    burnout_counts, 
    values="count", 
    names="burnout_level",
    color="burnout_level", 
    color_discrete_map=color_map,
    hole=0.45
)
fig.update_traces(textposition="inside", textinfo="percent+label")
fig.update_layout(showlegend=True, height=380)
st.plotly_chart(fig, width="stretch")
st.markdown("   ")

st.markdown(":rainbow-background[Avg Burnout Score by Work Model]")
burnout_mode = filtered.groupby("work_mode")["burnout_score"].mean().reset_index()
fig1 = px.bar(
    burnout_mode, 
    x="work_mode", 
    y="burnout_score",
    color="burnout_score", 
    color_continuous_scale="RdYlGn_r",
    text_auto=".2f", 
    labels={"burnout_score": "Avg Burnout Score", "work_mode": "Work Mode"}
)
fig1.update_layout(height=380, showlegend=False)
fig1.update_traces(textposition="outside")
st.plotly_chart(fig1,  width="stretch")
st.markdown("   ")

st.markdown(":rainbow-background[Avg Burnout Score by Job Role]")
burnout_role = (filtered.groupby("job_role")["burnout_score"].mean().sort_values(ascending=True).reset_index())
fig2 = px.bar(
    burnout_role, 
    x="burnout_score", 
    y="job_role",
    orientation="h", 
    color="burnout_score",
    color_continuous_scale="RdYlGn_r", 
    text_auto=".2f",
    labels={"burnout_score": "Avg Burnout Score", "job_role": "Job Role"}
)
fig2.update_layout(height=420, showlegend=False)
st.plotly_chart(fig2, width="stretch")
st.markdown("   ")

st.markdown(":rainbow-background[Burnout Level by Gender]")
burnout_gender = (filtered.groupby(["gender", "burnout_level"]).size().reset_index(name="count"))
fig3 = px.bar(
    burnout_gender, 
    x="gender", 
    y="count", 
    color="burnout_level",
    barmode="group",
    text_auto=True,
    color_discrete_map=color_map,
    labels={"count": "Number of Employees", "gender": "Gender"}
)
fig3.update_layout(height=420)
st.plotly_chart(fig3, width="stretch")

st.markdown("   ")
st.markdown(":rainbow-background[Work Hours vs Burnout Score]")
sample = filtered.sample(min(3000, len(filtered)), random_state=42)
fig4 = px.scatter(
    sample, 
    x="work_hours_per_week", 
    y="burnout_score",
    color="burnout_level", 
    color_discrete_map=color_map,
    opacity=0.6, 
    trendline="ols",
    labels={
        "work_hours_per_week": "Work Hours / Week",
        "burnout_score": "Burnout Score"}
)
fig4.update_layout(height=400)
st.plotly_chart(fig4, width="stretch")
st.markdown("   ")
st.markdown(":rainbow-background[Sleep Hours Distribution by Burnout Level]")

fig5 = px.box(
    filtered, 
    x="burnout_level", 
    y="sleep_hours",
    color="burnout_level", 
    color_discrete_map=color_map,
    labels={"sleep_hours": "Sleep Hours", "burnout_level": "Burnout Level"}
)
fig5.update_layout(height=400, showlegend=False)
st.plotly_chart(fig5, width="stretch")
st.markdown("   ")

st.markdown(":rainbow-background[Avg Burnout Score — Job Role × Company Size]")

pivot = (
    filtered.groupby(["job_role", "company_size"])["burnout_score"].mean().reset_index().pivot(index="job_role", columns="company_size", values="burnout_score")
)
fig6 = px.imshow(
    pivot, text_auto=".2f", 
    color_continuous_scale="RdYlGn_r",
    labels={"color": "Avg Burnout Score"}, 
    aspect="auto"
)
fig6.update_layout(height=450)
st.plotly_chart(fig6, width="stretch")
st.markdown("   ")

st.subheader("🔗 :green[Correlations]", divider="green")
st.markdown("   ")
st.subheader("🤖 :blue[Predictive Model]", divider="blue")
st.markdown("   ")
st.subheader("👥 :violet[Employee Segments]", divider="violet")
st.markdown("   ")
st.subheader("⚠️ :yellow[Risk Profiles]", divider="yellow")
st.markdown("   ")
# ============================================
# FOOTER
# ============================================
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <p><strong>🤯 Mental Health Burnout Analysis</strong></p>
    <p>Explore key metrics, risk factors, demographics and operations.</p>
    <p style='font-size: 0.9rem;'>Navigate using the sidebar to explore different datasets</p>
</div>
""", unsafe_allow_html=True)
