import streamlit as st
import pandas as pd
import requests
import pydeck as pdk
from background import add_bg_from_local

add_bg_from_local('APP/background_images/background.gif')

# Load the data
data = pd.read_csv('APP/REPORTED_DATA.csv', parse_dates=[0])

st.markdown("""
<div style='text-align: center;'>
    <h1> Report Map </h2>
</div>
""", unsafe_allow_html=True)

# Function to get user's location based on IP address
def get_user_location():
    response = requests.get("https://ipinfo.io")
    data = response.json()
    location = data['loc'].split(',')
    latitude = float(location[0])
    longitude = float(location[1])
    return latitude, longitude

# Get the user's location
current_latitude, current_longitude = get_user_location()
fixed_latitude, fixed_longitude = 51.5130,-0.0897

# Check if the data contains the required columns
if 'latitude' in data.columns and 'longitude' in data.columns:
    # Create a new dataframe for the map
    map_data = data[['latitude', 'longitude', 'category', 'comment']]
    map_data.columns = ['lat', 'lon', 'category', 'comment']
else:
    st.write("The CSV file does not contain 'latitude' and 'longitude' columns.")

# Add the user's location to the map data
user_location = pd.DataFrame({'lat': [current_latitude], 'lon': [current_longitude], 'category': ['Your Location'], 'comment': ['This is your current location']})
map_data = pd.concat([map_data, user_location], ignore_index=True)

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
    "html": "<b>Category:</b> {category} <br/><b>Comment:</b> {comment}",
    "style": {
        "backgroundColor": "steelblue",
        "color": "white",
    }
}

view_state = pdk.ViewState(latitude=fixed_latitude, longitude=fixed_longitude, zoom=12)
r = pdk.Deck(layers=[layer], 
             initial_view_state=view_state, 
             tooltip=tooltip,
             map_style='mapbox://styles/mapbox/light-v10',)
st.pydeck_chart(r)

st.markdown("""
<div style='text-align: center;'>
- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
</div>
""", unsafe_allow_html=True)

# Display the user's location
st.write(f"Your current location is: Latitude: {current_latitude}, Longitude: {current_longitude}")
st.write(f"NOTE: The location is identified based on the IP address, since steamlit servers are located at Dalles, Oregon, United States, you will find the current location to be wrong.")
st.markdown("""
<div style='text-align: center;'>
- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
</div>
""", unsafe_allow_html=True)

# Display the dataframe to inspect the columns
st.markdown("""
<div style='text-align: center;'>
    <h1> User Reports </h2>
</div>
""", unsafe_allow_html=True)

st.write(data)
# st.write(map_data)
