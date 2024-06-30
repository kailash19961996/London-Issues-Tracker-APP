import streamlit as st
import pandas as pd
import requests
import pydeck as pdk

# Load the data
data = pd.read_csv('REPORTED_DATA.csv', parse_dates=[0])

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

st.title('Maps')

# Display the user's location
st.write(f"Your location is: Latitude: {current_latitude}, Longitude: {current_longitude}")

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
        "color": "white"
    }
}

view_state = pdk.ViewState(latitude=current_latitude, longitude=current_longitude, zoom=12)
r = pdk.Deck(layers=[layer], initial_view_state=view_state, tooltip=tooltip)
st.pydeck_chart(r)

# Display the dataframe to inspect the columns
st.title('USER DATA')
st.write(data)
# st.write(map_data)

# Display the map
# st.map(map_data)