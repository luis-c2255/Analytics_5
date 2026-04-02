import streamlit as st
from utils.theme import Components

st.set_page_config(
        page_title=f"Spotify Wrapped 2025 Analysis",
        page_icon= "🎶",
        layout="wide",
        initial_sidebar_state="expanded"
    )
try:
    with open('style.css') as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
except FileNotFoundError:
    pass


st.markdown(
    Components.page_header("🎶 Spotify Wrapped 2025 Analysis"), unsafe_allow_html=True
)

# ============================================
# FOOTER
# ============================================
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <p><strong>🎶 Spotify Wrapped 2025 Analysis</strong></p>
    <p>Comprehensive analysis of Netflix's content library</p>
    <p style='font-size: 0.9rem;'>Navigate using the sidebar to explore different datasets</p>
</div>
""", unsafe_allow_html=True)
