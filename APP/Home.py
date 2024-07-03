import streamlit as st
import os
import time
from datetime import datetime
from PIL import Image
import openai
import requests
import pandas as pd
import base64
from io import BytesIO
import pydeck as pdk
from background import add_bg_from_local, show_gif_overlay, get_geolocation, classify_image

# Set OpenAI API key
api_key = st.secrets["openai"]["api_key"]
if api_key is None:
    raise ValueError("API key not found. Please set the OPENAI_API_KEY environment variable.")
openai.api_key = api_key

add_bg_from_local('APP/background_images/whitebgs.jpg')

logo = Image.open("APP/background_images/logo_wihtout_background.png")
buffered = BytesIO()
logo.save(buffered, format="PNG")
logo_base64 = base64.b64encode(buffered.getvalue()).decode()

# CSS to center the logo and title
st.markdown(f"""
    <style>
    .centered {{
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
    }}
    .centered img {{
        width: 100px;
    }}
    </style>
    <div class="centered">
        <img src="data:image/png;base64,{logo_base64}" alt="Logo">
        <h1>London Issue Tracker</h1>
    </div>
    """, unsafe_allow_html=True)

st.markdown("""
<div style='text-align: center;'>
     "The app allows users to report, view, and track urban issues in real-time, helping to improve community spaces through AI-driven insights."
</div>
""", unsafe_allow_html=True)

latitude, longitude = 51.5074456, -0.1277653 # London
# Initialize session state for latitude and longitude if not already done
if 'latitude' not in st.session_state:
    st.session_state.latitude = latitude
if 'longitude' not in st.session_state:
    st.session_state.longitude = longitude

# File uploader
uploaded_file = st.file_uploader("Start by uploading an image...", type=['png', 'jpg', 'jpeg', 'webp', 'heic'])

# Define categories
categories = [
    "graffiti",
    "garbage",
    "broken_window",
    "green_spaces",
    "public_buildings",
    "sports_and_social_events"
]

# Directory setup for images
images_dir = "REPORTED_IMAGES"
if not os.path.exists(images_dir):
    os.makedirs(images_dir)

# CSV setup
csv_path = "APP/REPORTED_DATA.csv"
if not os.path.exists(csv_path):
    with open(csv_path, 'w') as f:
        f.write("timestamp,latitude,longitude,category,image_path,comment\n")

# Function to save image data to CSV
def save_image_data(timestamp, latitude, longitude, image_path, category, comment):
    with open(csv_path, 'a') as f:
        f.write(f"{timestamp},{latitude},{longitude},{category},{image_path},{comment}\n")

# Main app logic
if uploaded_file is not None:
    image = Image.open(uploaded_file)
    new_size = (250, 250)
    resized_image = image.resize(new_size)
    st.image(resized_image, caption='Uploaded Image.', use_column_width=False)

    # Classify the image
    category = classify_image(image)
    image_path = os.path.join(images_dir, uploaded_file.name)
    st.success(f'Classification : {category}')

    if category not in categories:
        sample_image_path = 'APP/sample_image/graffiti.jpg'  # Path to sample image
        if os.path.exists(sample_image_path):
            with open(sample_image_path, "rb") as file:
                st.write(f"NOTE : As of now, the model is designed to detect only these 6 categories: ")
                st.write(f"Graffiti, Garbage, Broken Window, Green Spaces, Public Buildings, Sports and Social events")
                st.write(f"Please upload an image that fits one of the above category. If you are not sure what to upload, download the sample image below.")
                btn = st.download_button(
                    label="Download a sample image",
                    data=file,
                    file_name="sample.jpg",
                    mime="image/jpeg")
                st.write(f"Read the documentation on Github repo for more info.")
    else:
        with st.form(key='report_form'):
            comment = st.text_input("Add a comment about the image:")
            address = st.text_input("Enter your PINCODE or street name or city:")
            submit_button = st.form_submit_button(label='Submit')

        if submit_button:
            if comment and address:
                timestamp = datetime.now()
                formatted_timestamp = timestamp.strftime('%Y-%m-%d %H:%M:%S')
                latitude, longitude, area_name = get_geolocation(address)
                if latitude is not None and longitude is not None:
                    # Store the latitude and longitude in session state
                    st.session_state.latitude = latitude
                    st.session_state.longitude = longitude
                    st.success(f"Latitude: {latitude}, Longitude: {longitude}")
                    st.info(f"Area Name: {area_name}")
                    sanitized_comment = comment.replace(',', '')  # Remove all commas from the comment
                    image.save(image_path)
                    save_image_data(formatted_timestamp, latitude, longitude, image_path, category, sanitized_comment)
                    st.success('Thanks for reporting your thoughts, we will look into it.')
                    show_gif_overlay('APP/background_images/stars2.gif', duration=3)
                else:
                    st.error("Could not find geolocation for the provided address. Please check your address again")
            else:
                st.error('Please add a comment and enter your address before submitting.')

st.markdown("""
    <style>
    .centered {
        text-align: center;
        margin: 0 auto;
    }
    </style>
    <div class="centered">
        <h2>Interactive Live Map</h2>
    </div>
    <div class="centered">
        Hover over the red spots for more info
    </div>
    """, unsafe_allow_html=True)

# Load the data
data = pd.read_csv('APP/REPORTED_DATA.csv', parse_dates=[0])

# Check if the data contains the required columns
if 'latitude' in data.columns and 'longitude' in data.columns:
    # Create a new dataframe for the map
    map_data = data[[ 'timestamp', 'latitude', 'longitude', 'category', 'comment']]
    map_data.columns = ['timestamp', 'lat', 'lon', 'category', 'comment']
    map_data['timestamp'] = map_data['timestamp'].astype(str)
else:
    st.write("The CSV file does not contain 'latitude' and 'longitude' columns.")

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

