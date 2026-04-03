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

st.subheader("🔗 :green[Correlation & Driver Analysis]", divider="green")
st.markdown("   ")
st.markdown(":green-background[Feature Correlation Matrix]")

numeric_df = filtered.select_dtypes(include=np.number)
corr = numeric_df.corr()

fig7 = px.imshow(
    corr, 
    text_auto=".2f", 
    color_continuous_scale="RdBu_r",
    zmin=-1, zmax=1, aspect="auto",
    labels={"color": "Correlation"}
)
fig7.update_layout(height=600)
fig7.update_traces(textfont_size=8)
st.plotly_chart(fig7, width="stretch")

st.markdown("   ")
st.markdown(":green-background[Top Drivers of Burnout Score]")
burnout_corr = (
    corr["burnout_score"].drop("burnout_score").sort_values(key=abs, ascending=False).head(12).reset_index())
burnout_corr.columns = ["feature", "correlation"]
burnout_corr["color"] = burnout_corr["correlation"].apply(lambda x: "#e74c3c" if x > 0 else "#2ecc71")
fig8 = px.bar(
    burnout_corr, 
    x="correlation", 
    y="feature",
    orientation="h", 
    color="color",
    color_discrete_map="identity", 
    text_auto=".2f",
    labels={"correlation": "Pearson Correlation", "feature": "Feature"}
)
fig8.update_layout(height=450, showlegend=False)
fig8.update_traces(textposition="outside")
st.plotly_chart(fig8, width="stretch")
st.markdown("   ")
st.markdown(":green-background[Mental Health Score Distributions]")
mental_cols = ["stress_level", "anxiety_score", "depression_score", "burnout_score"]
fig9 = go.Figure()
colors = ["#e74c3c", "#f39c12", "#9b59b6", "#3498db"]
for col, color in zip(mental_cols, colors):
    fig9.add_trace(go.Violin(
        y=filtered[col], name=col.replace("_", " ").title(),
        box_visible=True, meanline_visible=True,
        fillcolor=color, opacity=0.7,
        line_color="white"
    ))
    fig9.update_layout(
        height=450, showlegend=True,
        yaxis_title="Score",
        violingap=0.2, violinmode="overlay"
    )
    st.plotly_chart(fig9, width="stretch")

st.markdown("   ")
st.markdown(":green-background[Pairwise Relationships — Key Variables]")
pair_cols = ["work_hours_per_week", "sleep_hours", "stress_level",
             "anxiety_score", "burnout_score", "work_life_balance"]
sample_pair = filtered.sample(min(2000, len(filtered)), random_state=42)
fig10 = px.scatter_matrix(
    sample_pair, dimensions=pair_cols,
    color="burnout_level", color_discrete_map=color_map,
    opacity=0.4,
    labels={col: col.replace("_", " ").title() for col in pair_cols}
)
fig10.update_traces(diagonal_visible=False, showupperhalf=False, marker=dict(size=3))
fig10.update_layout(height=600)
st.plotly_chart(fig10, width="stretch")

st.markdown("   ")
st.markdown(":green-background[Overtime Hours vs Burnout Score]")
sample_ot = filtered.sample(min(3000, len(filtered)), random_state=42)
fig11 = px.scatter(
    sample_ot, x="overtime_hours", y="burnout_score",
    color="work_mode", trendline="ols",
    opacity=0.6,
    labels={
        "overtime_hours": "Overtime Hours",
        "burnout_score": "Burnout Score",
        "work_mode": "Work Mode"}
)
fig11.update_layout(height=400)
st.plotly_chart(fig11, width="stretch")

st.markdown("   ")
st.markdown(":green-background[Work-Life Balance vs Burnout Score]")

fig12 = px.scatter(
    sample_ot, x="work_life_balance", y="burnout_score",
    color="burnout_level", color_discrete_map=color_map,
    trendline="ols", opacity=0.6,
    labels={
        "work_life_balance": "Work-Life Balance Score",
        "burnout_score": "Burnout Score"}
)
fig12.update_layout(height=400)
st.plotly_chart(fig12, width="stretch")
st.markdown("   ")
st.markdown(":green-background[Screen Time vs Anxiety Score]")
fig13 = px.scatter(
    sample_ot, x="screen_time_hours", y="anxiety_score",
    color="burnout_level", color_discrete_map=color_map,
    trendline="ols", opacity=0.6,
    labels={
        "screen_time_hours": "Screen Time (Hours/Day)",
        "anxiety_score": "Anxiety Score"}
)
fig13.update_layout(height=400)
st.plotly_chart(fig13, width="stretch")
st.markdown("   ")
st.markdown(":green-background[Caffeine Intake vs Stress Level]")
caffeine_stress = (filtered.groupby("caffeine_intake")["stress_level"].mean().reset_index())
fig14 = px.bar(
    caffeine_stress, x="caffeine_intake", y="stress_level",
    color="stress_level", color_continuous_scale="RdYlGn_r",
    text_auto=".2f",
    labels={
        "caffeine_intake": "Caffeine Intake (cups/day)",
        "stress_level": "Avg Stress Level"}
)
fig14.update_layout(height=400, showlegend=False)
st.plotly_chart(fig14, width="stretch")
st.markdown("   ")

st.subheader("🤖 :blue[Burnout Prediction — Random Forest Model]", divider="blue")
st.markdown("#### Train a Random Forest model to predict burnout level and identify the most important features.")
st.markdown("   ")

# Model config
col1, col2, col3 = st.columns(3)
with col1:
    n_estimators = st.slider("Number of Trees", 50, 300, 100, step=50)
with col2:
    max_depth = st.slider("Max Tree Depth", 3, 20, 8)
with col3:
    test_size = st.slider("Test Set Size (%)", 10, 40, 20, step=5)
    
train_model = st.button("🚀 Train Model", type="primary")

if train_model:
    with st.spinner("Training Random Forest model on your dataset..."):
        model_df = filtered.copy()
        # Encode categorical columns
        le = LabelEncoder()
        cat_cols_model = ["gender", "job_role", "company_size", "work_mode"]
        for col in cat_cols_model:
            model_df[col] = le.fit_transform(model_df[col].astype(str))
    
            # Encode target
            level_map = {"Low": 0, "Moderate": 1, "High": 2}
            model_df["burnout_level_enc"] = model_df["burnout_level"].map(level_map)

            feature_cols = [
                "age", "gender", "job_role", "experience_years", "company_size",
                "work_mode", "work_hours_per_week", "overtime_hours", "meetings_per_day",
                "deadlines_missed", "job_satisfaction", "manager_support",
                "work_life_balance", "sleep_hours", "physical_activity_days",
                "screen_time_hours", "caffeine_intake", "social_support_score",
                "has_therapy", "stress_level", "anxiety_score", "depression_score"
                ]
            X = model_df[feature_cols]
            y_clf = model_df["burnout_level_enc"]
            y_reg = model_df["burnout_score"]
            
            X_train, X_test, y_clf_train, y_clf_test, y_reg_train, y_reg_test = train_test_split(X, y_clf, y_reg, test_size=test_size / 100, random_state=42)
            # ── Train Classifier ──
            clf = RandomForestClassifier(
                n_estimators=n_estimators,
                max_depth=max_depth,
                random_state=42,
                n_jobs=-1
            )
            clf.fit(X_train, y_clf_train)
            y_clf_pred = clf.predict(X_test)
            
            # ── Train Regressor ──
            reg = RandomForestRegressor(
                n_estimators=n_estimators,
                max_depth=max_depth,
                random_state=42,
                n_jobs=-1
            )
            reg.fit(X_train, y_reg_train)
            y_reg_pred = reg.predict(X_test)
            r2 = r2_score(y_reg_test, y_reg_pred)
            
# ── Classification Report ──
report = classification_report(
    y_clf_test, y_clf_pred,
    target_names=["Low", "Moderate", "High"],
    output_dict=True
)
report_df = pd.DataFrame(report).transpose().round(3)
st.success("✅ Model trained successfully!")

# ── Model Performance KPIs ──
m1, m2, m3, m4 = st.columns(4)
with m1:
    st.markdown(
        Components.metric_card(
            title="Classifier Accuracy",
            value=f"{report['accuracy']:.2%}",
            delta="🎯",
            card_type="info"
        ), unsafe_allow_html=True
    )
with m2:
    st.markdown(
        Components.metric_card(
            title="Regression R² Score",
            value=f"{r2:.4f}",
            delta="📊",
            card_type="warning"
        ), unsafe_allow_html=True
    )
with m3:
    st.markdown(
        Components.metric_card(
            title="Trees Trained",
            value=f"{n_estimators}",
            delta="🌲",
            card_type="success"
        ), unsafe_allow_html=True
    )
with m4:
    st.markdown(
        Components.metric_card(
            title="Test Samples",
            value=f"{len(y_clf_test):,}",
            delta="🧪",
            card_type="success"
        ), unsafe_allow_html=True
    )
st.markdown("   ")
st.markdown("🔑 :blue-background[Top Feature Importances (Classifier)]")

feat_imp = pd.DataFrame({
    "feature": feature_cols,
    "importance": clf.feature_importances_
}).sort_values("importance", ascending=True).tail(15)

fig15 = px.bar(
    feat_imp, x="importance", y="feature",
    orientation="h", color="importance",
    color_continuous_scale="Blues",
    text_auto=".3f",
    labels={"importance": "Feature Importance", "feature": "Feature"}
)
fig15.update_layout(height=500, showlegend=False)
fig15.update_traces(textposition="outside")
st.plotly_chart(fig15, width="stretch")

st.markdown("   ")
st.markdown("🔑 :blue-background[Top Feature Importances (Regressor)]")

feat_imp_reg = pd.DataFrame({
    "feature": feature_cols,
    "importance": reg.feature_importances_
}).sort_values("importance", ascending=True).tail(15)

fig16 = px.bar(
    feat_imp_reg, x="importance", y="feature",
    orientation="h", color="importance",
    color_continuous_scale="Oranges",
    text_auto=".3f",
    labels={"importance": "Feature Importance", "feature": "Feature"}
)
fig16.update_layout(height=500, showlegend=False)
fig16.update_traces(textposition="outside")
st.plotly_chart(fig16, width="stretch")

st.markdown("   ")
st.markdown("📋 :blue-background[Classification Report]")
st.dataframe(report_df.style.background_gradient(cmap="Blues", subset=["precision", "recall", "f1-score"]),width="stretch")

st.markdown("   ")
st.markdown("📈 :blue-background[Actual vs Predicted Burnout Score]")

pred_df = pd.DataFrame({
    "Actual": y_reg_test.values,
    "Predicted": y_reg_pred
}).sample(min(1000, len(y_reg_test)), random_state=42)

fig17 = px.scatter(
    pred_df, x="Actual", y="Predicted",
    opacity=0.5, trendline="ols",
    color_discrete_sequence=["#3498db"],
    labels={"Actual": "Actual Burnout Score", "Predicted": "Predicted Burnout Score"}
)
fig17.add_shape(
    type="line", x0=pred_df["Actual"].min(), y0=pred_df["Actual"].min(),
    x1=pred_df["Actual"].max(), y1=pred_df["Actual"].max(),
    line=dict(color="red", dash="dash", width=2)
)
fig17.update_layout(height=450)
st.plotly_chart(fig17, width="stretch")

st.markdown("   ")
st.markdown("🔢 :blue-background[Confusion Matrix]")

from sklearn.metrics import confusion_matrix
cm = confusion_matrix(y_clf_test, y_clf_pred)
cm_df = pd.DataFrame(
    cm,
    index=["Actual: Low", "Actual: Moderate", "Actual: High"],
    columns=["Pred: Low", "Pred: Moderate", "Pred: High"]
)
fig18 = px.imshow(
    cm_df, text_auto=True,
    color_continuous_scale="Blues",
    labels={"color": "Count"},
    aspect="auto"
)
fig18.update_layout(height=400)
st.plotly_chart(fig18, width="stretch")

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
