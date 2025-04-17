import streamlit as st
import requests
import plotly.graph_objects as go
import folium
from streamlit_folium import st_folium
from waqi import fetch_aqi  # function to get air quality data from WAQI API

# This function assigns a color and label based on AQI value
def aqi_color(aqi):
    if aqi <= 50: return "Good", "green"
    elif aqi <= 100: return "Moderate", "yellow"
    elif aqi <= 150: return "Unhealthy for Sensitive Groups", "orange"
    elif aqi <= 200: return "Unhealthy", "red"
    elif aqi <= 300: return "Very Unhealthy", "purple"
    return "Hazardous", "maroon"

# This gives health advice depending on the AQI value
def aqi_advice(aqi):
    if aqi <= 50:
        return "Air is clean. Great day to go outside!"
    elif aqi <= 100:
        return "Air is acceptable. Sensitive groups can still go out, but take it easy."
    elif aqi <= 150:
        return "Unhealthy for sensitive people. Limit outdoor activities."
    elif aqi <= 200:
        return "Unhealthy. Everyone should reduce prolonged outdoor exertion."
    elif aqi <= 300:
        return "Very unhealthy. Stay indoors if possible."
    return "Hazardous. Avoid all outdoor activity."

# This function tries to detect the user's city based on their IP address
@st.cache_data
def detect_city():
    try:
        info = requests.get("https://ipinfo.io", timeout=3).json()  # call IP info API
        return info.get("city")  # extract city name
    except:
        return None  # return nothing if the API fails

# This is the main function that shows the AQI based on user's location
def show_ip_location():
    st.subheader("📍 Check by My Location (Auto-detected)")

    city = detect_city()  # Get the city name based on IP

    if city:
        # Show a message with the detected city
        st.success(f"📍 Detected city: **{city}**")

        # Use that city to get the AQI data from the WAQI API
        data = fetch_aqi(city)

        if data:
            aqi = data["aqi"]  # The air quality index value
            label, color = aqi_color(aqi)  # Get label and color based on AQI

            # Show the AQI number and air quality category
            st.markdown(f"**AQI:** {aqi}  \n"
                        f"**Air Quality:** <span style='color:{color}; font-weight:bold'>{label}</span>",
                        unsafe_allow_html=True)

            # Show a health advice message
            st.info(aqi_advice(aqi))

            # Gauge chart and legend side by side
            col1, col2 = st.columns([3, 1], gap="large")

            with col1:
                fig = go.Figure(go.Indicator(
                    mode="gauge+number",
                    value=aqi,
                    title={"text": "Air Quality Index"},
                    gauge={
                        "axis": {"range": [0, 500]},  # AQI goes from 0 to 500
                        "bar": {"color": "rgba(0,0,0,0)"},  # makes the center transparent
                        "steps": [  # colors for different AQI levels
                            {"range": [0, 50], "color": "green"},
                            {"range": [51, 100], "color": "yellow"},
                            {"range": [101, 150], "color": "orange"},
                            {"range": [151, 200], "color": "red"},
                            {"range": [201, 300], "color": "purple"},
                            {"range": [301, 500], "color": "maroon"},
                        ],
                        "threshold": {  # Show an indicator arrow
                            "line": {"color": color, "width": 4},
                            "value": aqi
                        }
                    }
                ))
                # Show the chart on screen
                st.plotly_chart(fig, use_container_width=True)

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

            # Get the coordinates of the city
            lat, lon = data.get("lat"), data.get("lon")
            if lat and lon:
                st.subheader("Location on Map")
                # Show map centered on the detected city
                m = folium.Map(location=[lat, lon], zoom_start=4, tiles="OpenStreetMap")
                # Add a pin with AQI info
                folium.Marker(
                    [lat, lon],
                    tooltip=city,
                    popup=f"AQI: {aqi}",
                    icon=folium.Icon(color="red" if aqi > 100 else "green")
                ).add_to(m)
                # Display the map in the app
                st_folium(m, width=700, height=500)

        else:
            # If the WAQI API didn’t return data
            st.error("Could not fetch AQI data for your city.")
    else:
        # If the IP-based city detection failed
        st.warning("Could not detect your city via IP.")