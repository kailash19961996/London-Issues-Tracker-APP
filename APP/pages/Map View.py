import streamlit as st
import pandas as pd
import requests
import pydeck as pdk
from background import add_bg_from_local, get_geolocation, show_gif_overlay
from Home import api_key
from PIL import Image

add_bg_from_local('APP/background_images/background.gif')

logo = Image.open("APP/background_images/logo_wihtout_background.png")
# Create columns to align the logo left of the title
col1, col2 = st.columns([1, 5])
with col1:
    st.image(logo, width=100)
with col2:
    st.title("Reports by Location")

st.markdown("""
<div style='text-align: center;'>
"Real-time interactive maps display user-reported urban issues, providing a clear visualization of local challenges."        
</div>
""", unsafe_allow_html=True)

latitude, longitude = 51.5074456, -0.1277653 # London
if 'latitude' not in st.session_state:
    st.session_state.latitude = latitude
if 'longitude' not in st.session_state:
    st.session_state.longitude = longitude

# Load the data
data = pd.read_csv('APP/REPORTED_DATA.csv', parse_dates=[0])
if 'latitude' in data.columns and 'longitude' in data.columns:
    map_data = data[[ 'timestamp', 'latitude', 'longitude', 'category', 'comment']]
    map_data.columns = ['timestamp', 'lat', 'lon', 'category', 'comment']
    map_data['timestamp'] = map_data['timestamp'].astype(str)
else:
    st.write("The CSV file does not contain 'latitude' and 'longitude' columns.")

with st.form(key='report_form'):
            address = st.text_input("Enter your PINCODE to find the reports nearby your area:")
            submit_button = st.form_submit_button(label='Submit')
if submit_button:
    if address:
        latitude, longitude, area_name = get_geolocation(address)
        if latitude is not None and longitude is not None:
            # Store the latitude and longitude in session state
            st.session_state.latitude = latitude
            st.session_state.longitude = longitude
            st.info(f"Area Name: {area_name}, Latitude: {latitude}, Longitude: {longitude}")
        else:
            st.error("Could not find geolocation for the provided address. Please check your PINCODE again")
    else:
        st.error('Enter your PINCODE before submitting.')

# Display the map using pydeck
layer = pdk.Layer(
    'ScatterplotLayer',
    data=map_data,
    get_position='[lon, lat]',
    get_fill_color='[200, 30, 0, 160]',
    get_radius=100,
    pickable=True,
    auto_highlight=True
)

tooltip = {
    "html": "<b>Category:</b> {category} <br/><b>Comment:</b> {comment}<br/><b>Report Time:</b> {timestamp} <br/>",
    "style": {
        "backgroundColor": "steelblue",
        "color": "white",
    }
}

view_state = pdk.ViewState(latitude=latitude, longitude=longitude, zoom=12)
r = pdk.Deck(layers=[layer], 
             initial_view_state=view_state, 
             tooltip=tooltip,
             map_style='mapbox://styles/mapbox/light-v10',)
st.pydeck_chart(r)
st.write(f"Latitude: {latitude}, Longitude: {longitude}")

# Display the dataframe to inspect the columns
st.markdown("""
<div style='text-align: center;'>
    <h1> User Reports </h2>
</div>
""", unsafe_allow_html=True)

st.write(data)
