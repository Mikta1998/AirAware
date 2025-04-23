import streamlit as st
from search import aqi_color


def remove_city(city):
    '''
    Callback to remove a city.
    '''
    st.session_state.favorites.pop(city, None)
    st.session_state[f"confirming_{city}"] = False

def show_fav_cities():
    '''
    This function shows how the favourite city is saved in the favourite site.
    '''
    st.title("⭐ Your favourite cities")

    if "favorites" not in st.session_state:
        st.session_state.favorites = {}

    if not st.session_state.favorites:
        st.info("You haven't saved your favourite city yet.")
        return

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

                st.markdown(
                    f"""
                    <div class="fav-card">
                        <h4 style="margin-bottom:0.2em;">{city}</h4>
                        <div style="font-size:1.1em;margin-bottom:0.6em;">
                            <b>AQI:</b> {aqi}<br>
                            <b>Status:</b> <span style="color:{color};">{label}</span>
                        </div>
                        <div style="font-size:0.97em; margin-bottom:0.4em;">
                            <b>Empfehlung:</b><br>
                            <span style="color:#eee;">{advice}</span>
                        </div>
                        <div style="font-size:0.93em; color:#eee;">
                            <b>Koordinaten:</b> {lat}, {lon}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                confirm_key = f"confirming_{city}"
                if confirm_key not in st.session_state:
                    st.session_state[confirm_key] = False

                if st.session_state[confirm_key]:
                    st.warning(f"Do you want to remove **{city}** out of your favourite list?")
                    col_confirm, col_cancel = st.columns(2)
                    with col_confirm:
                        if st.button("✅ Yes", key=f"yes_{city}"):
                            remove_city(city)
                            st.rerun()
                    with col_cancel:
                        if st.button("❌ No", key=f"no_{city}"):
                            st.session_state[confirm_key] = False
                            st.rerun()
                else:
                    if st.button("✕", key=f"remove_btn_{city}", help="Remove"):
                        st.session_state[confirm_key] = True
                        st.rerun()
