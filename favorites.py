import streamlit as st
from search import aqi_color


def remove_city(city):
    '''
    Callback function to remove a city from the favourites list.
    '''
    st.session_state.favorites.pop(city, None)
    st.session_state[f"confirming_{city}"] = False

def show_fav_cities():
    '''
    Display the user's favourite cities along with AQI data.
    '''
    st.title("⭐ Your favourite cities")

    # initializes the favourite list if not already in session state
    if "favorites" not in st.session_state:
        st.session_state.favorites = {}

    if not st.session_state.favorites:
        st.info("You haven't saved your favourite city yet.")
        return

    # using CSS to style saved cities in the favourite list
    st.markdown(
        """
        <style>
        .fav-card {
            background: #23272b;
            color: #eee;
            border-radius: 18px;
            box-shadow: 0 2px 12px rgba(0,0,0,0.10);
            padding: 1.2em 1.4em;
            border: 1.5px solid #bbb;
            min-height: 200px;
            margin-bottom: 1em;
        }
        .stButton > button {
            background: none !important;
            color: #eee !important;
            border: none !important;
            font-size: 1.5em !important;
            padding: 0 !important;
            margin: 0 !important;
            box-shadow: none !important;
            cursor: pointer;
        }
        .stButton > button:hover {
            color: #f53803 !important;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    # display favourite cities in two columns
    fav_list = list(st.session_state.favorites.items())
    n_cols = 2

    for i in range(0, len(fav_list), n_cols):
        cols = st.columns(n_cols)
        for j, (city, data) in enumerate(fav_list[i:i + n_cols]):
            with cols[j]:
                aqi = data.get('aqi', '-')
                advice = data.get('advice', '-')
                lat = data.get('lat', '-')
                lon = data.get('lon', '-')
                label, color = aqi_color(aqi)

                # render saved cities with AQI data in original colour from AQI website
                st.markdown(
                    f"""
                    <div class="fav-card">
                        <h4 style="margin-bottom:0.2em;">{city}</h4>
                        <div style="font-size:1.1em;margin-bottom:0.6em;">
                            <b>AQI:</b> {aqi}<br>
                            <b>Status:</b> <span style="color:{color};">{label}</span>
                        </div>
                        <div style="font-size:0.97em; margin-bottom:0.4em;">
                            <b>Recommendation:</b><br>
                            <span style="color:#eee;">{advice}</span>
                        </div>
                        <div style="font-size:0.93em; color:#eee;">
                            <b>Coordinates:</b> {lat}, {lon}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                # confirmation flow for removing a city
                confirm_key = f"confirming_{city}"
                if confirm_key not in st.session_state:
                    st.session_state[confirm_key] = False

                if st.session_state[confirm_key]:
                    st.warning(f"Do you want to remove **{city}** out of your favourite list?")
                    col_confirm, col_cancel = st.columns(2)

                    # button to confirm deletion of a city
                    with col_confirm:
                        if st.button("Yes", key=f"yes_{city}"):
                            remove_city(city)
                            st.rerun()

                    # button to cancel deletion of a city
                    with col_cancel:
                        if st.button("No", key=f"no_{city}"):
                            st.session_state[confirm_key] = False
                            st.rerun()
                else:
                    if st.button("✕", key=f"remove_btn_{city}", help="Remove"):
                        st.session_state[confirm_key] = True
                        st.rerun()
