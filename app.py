import streamlit as st
from utils.theme import Components

st.set_page_config(
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title(":orange[Multiple Dataset Analysis]", text_alignment="center")

with st.container(height="content", width="stretch", horizontal_alignment="center"):    
    st.image("utils/image.svg")
   
col1,  col2, col3 = st.columns(3)
with col1:
    st.link_button("Netflix Content Analysis",
    "https:",
    icon="📽️", icon_position="left", width="stretch"
    )
with col2:
    st.link_button("Online Shoppers Purchasing",
    "https:",
    icon="🛍️", icon_position="left", width="stretch"
    )
with col3:
    st.link_button("Global Volcano Eruption",
    "https:",
    icon="🌋", icon_position="left", width="stretch"
    )
col4, col5, col6, col7 = st.columns(4)
with col4:
    st.link_button("Pypi AI Packages Download",
    "https:",
    icon="🖥️", icon_position="left", width="stretch"
    )
with col5:
    st.link_button("Amazon Sales Analysis",
    "https:",
    icon="🛒", icon_position="left", width="stretch"
    )
with col6:
    st.link_button("Mental Health Burnout",
    "https:",
    icon="🤯", icon_position="left", width="stretch"
    )
with col7:
    st.link_button("Spotify Wrapped 2025",
    "https:",
    icon="🎶", icon_position="left", width="stretch"
    )

# ============================================
# FOOTER
# ============================================
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <p><strong>📊 Multiple Analysis Dashboard</strong></p>
    <p>Multiple Dashboards from several datasets analyzed</p>
    <p style='font-size: 0.9rem;'>Navigate using the sidebar to explore different datasets</p>
</div>
""", unsafe_allow_html=True)
