import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import folium
from streamlit_folium import st_folium
from waqi import fetch_aqi  # Function to get live AQI data via API

# Air Quality Index categories and colors
def aqi_color(aqi):
    if aqi <= 50: return "Good", "green"
    elif aqi <= 100: return "Moderate", "yellow"
    elif aqi <= 150: return "Unhealthy for Sensitive Groups", "orange"
    elif aqi <= 200: return "Unhealthy", "red"
    elif aqi <= 300: return "Very Unhealthy", "purple"
    return "Hazardous", "maroon"

# Gives advice based on Air Quality Index level
def aqi_advice(aqi):
    if aqi <= 50:
        return "Air is clean. Great day to go outside!"
    elif aqi <= 100:
        return "Air is acceptable. Sensitive groups can still go out, but take it easy."
    elif aqi <= 150:
        return "Unhealthy for sensitive people (asthma, elderly). Limit outdoor activities."
    elif aqi <= 200:
        return "Unhealthy. Everyone should reduce prolonged outdoor exertion."
    elif aqi <= 300:
        return "Very unhealthy. Stay indoors with windows closed if possible."
    return "Hazardous. Avoid all outdoor activity. Use air purifiers if available."

# Main search function
def show_search():
    st.subheader("Check Air Quality by City")

    # Text input for the user to type a city name
    city = st.text_input("Enter a city name")

    # Start with default values
    aqi = None
    label = None
    color = None
    advice = None
    lat, lon = 20, 0  # Default map center

    # If a city is entered, fetch real data
    if city:
        with st.spinner("Fetching air quality data..."):
            data = fetch_aqi(city)
        if data:
            aqi = data["aqi"]
            label, color = aqi_color(aqi)
            advice = aqi_advice(aqi)
            lat = data.get("lat", lat)
            lon = data.get("lon", lon)
        else:
            st.error("Could not fetch data for this city.")

    # Show AQI and label only if data exists
    if aqi is not None and label:
        st.markdown(f"**AQI:** {aqi}  \n"
                    f"**Air Quality:** <span style='color:{color}; font-weight:bold'>{label}</span>",
                    unsafe_allow_html=True)
        st.info(f"💡 {advice}")
    else:
        st.markdown("**AQI:**  \n**Air Quality:**")

    # Gauge + legend (always shown)
    col1, col2 = st.columns([3, 1], gap="large")
    with col1:
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=aqi if aqi is not None else 0,
            title={"text": "Air Quality Index", "font": {"size": 22}},
            gauge={
                "axis": {"range": [0, 500], "tickwidth": 2, "tickcolor": "white"},
                "bar": {"color": "rgba(0,0,0,0)", "thickness": 0.1},
                "steps": [
                    {"range": [0, 50], "color": "green"},
                    {"range": [51, 100], "color": "yellow"},
                    {"range": [101, 150], "color": "orange"},
                    {"range": [151, 200], "color": "red"},
                    {"range": [201, 300], "color": "purple"},
                    {"range": [301, 500], "color": "maroon"},
                ],
                "threshold": {
                    "line": {"color": color if color else "green", "width": 4},
                    "thickness": 0.75,
                    "value": aqi if aqi is not None else 0
                }
            },
            domain={"x": [0, 1], "y": [0, 1]}
        ))
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", font={"color": "white"})
        st.plotly_chart(fig, use_container_width=True)

    # AQI color guide legend
    with col2:
        st.markdown("""
        <div style='padding-top: 1rem;'>
            <strong>AQI Color Guide:</strong>
            <ul style='list-style-type: none; padding-left: 0; font-size: 0.9rem;'>
                <li><span style='color:green; font-weight: bold;'>■ 0-50:</span> Good</li>
                <li><span style='color:yellow; font-weight: bold;'>■ 51-100:</span> Moderate</li>
                <li><span style='color:orange; font-weight: bold;'>■ 101-150:</span> Unhealthy for Sensitive Groups</li>
                <li><span style='color:red; font-weight: bold;'>■ 151-200:</span> Unhealthy</li>
                <li><span style='color:purple; font-weight: bold;'>■ 201-300:</span> Very Unhealthy</li>
                <li><span style='color:maroon; font-weight: bold;'>■ 301-500:</span> Hazardous</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    # Map section
    st.subheader("Location on Interactive Map")
    m = folium.Map(location=[lat, lon], zoom_start=4 if city else 2, tiles="OpenStreetMap")
    if city and aqi is not None:
        folium.Marker(
            location=[lat, lon],
            tooltip=city,
            popup=f"AQI: {aqi}",
            icon=folium.Icon(color="red" if aqi > 100 else "green")
        ).add_to(m)
    st_folium(m, width=800, height=600)