import streamlit as st
from search import show_search              # Function for manual city AQI search
from ip_location import show_ip_location    # Function for IP-based AQI detection
from main_map import show_worldmap
from favorites import show_fav_cities
import folium
from streamlit_folium import st_folium

# Set app title and layout
st.set_page_config(page_title="Air Quality Dashboard", layout="wide")

# CSS for custom fonts and sidebar style
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600&display=swap');
    html, body, [class*="css"]  {
        font-family: 'Poppins', sans-serif;
    }
    [data-testid="stSidebar"] {
        background-color: #f8f8f800;
    }
    </style>
""", unsafe_allow_html=True)

# Sidebar menu for switching views
st.sidebar.title("Navigation")
page = st.sidebar.radio("Choose view:", ["Check a City", "Compare Capitals", "Check my Location", "My Favourite Cities"])

# Displays header at the top of every view
st.markdown("""
<div style="background: linear-gradient(to right, #4a90e2, #f06292); padding: 2rem; border-radius: 0.5rem;">
    <h1 style="color:white; font-size:2.5rem;">Global Air Quality Dashboard</h1>
    <p style="color:white;">Check real-time air quality across cities worldwide using live data from WAQI.</p>
    <h4 style="color:white; font-size:1.5rem;"> Description of AQI:</h4>
    <p style="color:white;">The Air Quality Index (AQI) is a standardized measure used to assess the level of air pollution at a specific location and time. \
        It is calculated based on the concentrations of key air pollutants such as particulate matter (PM2.5, PM10), ozone (O₃), carbon monoxide (CO), sulfur dioxide (SO₂), and nitrogen dioxide (NO₂). \
        The AQI typically ranges from 0 to 500, with higher values indicating poorer air quality and greater potential health risks. \
        The index is often color-coded to provide a clear and immediate indication of the health impact of the air quality on the general population.</p>
</div>
""", unsafe_allow_html=True)

# Shows the selected pages
if page == "Check a City":
    show_search()              # Displays manual search view
elif page == "Compare Capitals":
    show_worldmap()             # Displays the worldwide map with comparison
elif page == "Check my Location":
    show_ip_location()         # Displays auto-detect location view
elif page == "My Favourite Cities":
    show_fav_cities()           # Displays your favourite cities