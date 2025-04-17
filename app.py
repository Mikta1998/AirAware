import streamlit as st
from search import show_search              # Function for manual city AQI search
from ip_location import show_ip_location    # Function for IP-based AQI detection

# Set app title and layout
st.set_page_config(page_title="🌍 Air Quality Dashboard", layout="wide")

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
st.sidebar.title("🌍 Navigation")
page = st.sidebar.radio("Choose view:", ["Check by City", "Check by My Location"])

# Displays header at the top of every view
st.markdown("""
<div style="background: linear-gradient(to right, #4a90e2, #f06292); padding: 2rem; border-radius: 0.5rem;">
    <h1 style="color:white; font-size:2.5rem;">🌍 Global Air Quality Dashboard</h1>
    <p style="color:white;">Check real-time air quality across cities worldwide using live data from WAQI.</p>
</div>
""", unsafe_allow_html=True)

# Shows the selected view based on user choice
if page == "Check by City":
    show_search()              # Displays manual search view
elif page == "Check by My Location":
    show_ip_location()         # Displays auto-detect location view