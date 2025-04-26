import streamlit as st
from search import show_search
from main_map import show_worldmap
from favorites import show_fav_cities

# --- Streamlit page config ---
st.set_page_config(
    page_title="BreatheSafe Dashboard",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Sidebar navigation ---
st.sidebar.title("Navigation")
view = st.sidebar.radio("Choose view:", ("Check a City", "Compare Capitals", "My Favourite Cities"))

# --- Main area ---
if view == "Check a City":
    show_search()

elif view == "Compare Capitals":
    show_worldmap()

elif view == "My Favourite Cities":
    show_fav_cities()

# --- Footer ---
st.sidebar.markdown("---")
st.sidebar.caption("BreatheSafe © 2025 | Powered by WAQI Data")