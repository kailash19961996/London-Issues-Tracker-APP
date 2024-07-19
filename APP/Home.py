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


api_key = st.secrets["openai"]["api_key"]
if api_key is None:
    raise ValueError("API key not found. Please set the OPENAI_API_KEY environment variable.")
openai.api_key = api_key

add_bg_from_local('APP/background_images/whitebgs.jpg')

st.sidebar.caption(
    "Built by [Kai](https://kailashsubramaniyam.com/). Like this? [Hire me!](https://kailashsubramaniyam.com/contact)"
)


linkedin = "https://raw.githubusercontent.com/kailash19961996/icons-and-images/main/linkedin.gif"
github =   "https://raw.githubusercontent.com/kailash19961996/icons-and-images/main/github_transparent.gif"
Youtube =  "https://raw.githubusercontent.com/kailash19961996/icons-and-images/main/371907120_YOUTUBE_ICON_TRANSPARENT_1080.gif"
twitter =  "https://raw.githubusercontent.com/kailash19961996/icons-and-images/main/371907030_TWITTER_ICON_TRANSPARENT_1080.gif"
email =    "https://raw.githubusercontent.com/kailash19961996/icons-and-images/main/emails33.gif"
website =  "https://raw.githubusercontent.com/kailash19961996/icons-and-images/main/www.gif"


st.sidebar.caption(
    f"""
        <div style='display: flex; align-items: center;'>
            <div style='display: flex; align-items: center;'>
            <a href = 'https://kailashsubramaniyam.com/'><img src='{website}' style='width: 35px; height: 35px; margin-right: 25px;'></a>
            <a href = 'https://www.youtube.com/@kailashbalasubramaniyam2449/videos'><img src='{Youtube}' style='width: 28px; height: 28px; margin-right: 25px;'></a>
            <a href = 'https://www.linkedin.com/in/kailash-kumar-balasubramaniyam-62b075184'><img src='{linkedin}' style='width: 35px; height: 35px; margin-right: 25px;'></a>
            <a href = 'https://github.com/kailash19961996'><img src='{github}' style='width: 25px; height: 25px; margin-right: 25px;'></a>
            <a href = 'https://x.com/kylasben'><img src='{twitter}' style='width: 28px; height: 28px; margin-right: 25px;'></a>
            <a href = 'mailto:kailash.balasubramaniyam@gmail.com''><img src='{email}' style='width: 35px; height: 35px; margin-right: 25px;'></a>
        </div>""", unsafe_allow_html=True,)


coll1,coll2,coll3 = st.columns(3)
with coll2:
    st.write(
        f"""
            <div style='display: flex; align-items: center;'>
            <a href = 'https://kailashsubramaniyam.com/'><img src='{website}' style='width: 35px; height: 35px; margin-right: 25px;'></a>
            <a href = 'https://www.youtube.com/@kailashbalasubramaniyam2449/videos'><img src='{Youtube}' style='width: 28px; height: 28px; margin-right: 25px;'></a>
            <a href = 'https://www.linkedin.com/in/kailash-kumar-balasubramaniyam-62b075184'><img src='{linkedin}' style='width: 35px; height: 35px; margin-right: 25px;'></a>
            <a href = 'https://github.com/kailash19961996'><img src='{github}' style='width: 25px; height: 25px; margin-right: 25px;'></a>
            <a href = 'https://x.com/kylasben'><img src='{twitter}' style='width: 28px; height: 28px; margin-right: 25px;'></a>
            <a href = 'mailto:kailash.balasubramaniyam@gmail.com''><img src='{email}' style='width: 35px; height: 35px; margin-right: 25px;'></a>
        </div>""", unsafe_allow_html=True,)


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
        <h3>POWERED BY AI</h3>
    </div>
    """, unsafe_allow_html=True)

st.markdown("""
<div style='text-align: center;'>
     <i>"The app allows users to report, view, and track urban issues in real-time, helping to improve community spaces through AI-driven insights."<i>
</div>
""", unsafe_allow_html=True)

@st.experimental_dialog("How to use this APP", width=1920)
def show_video():
    video_url = "https://www.youtube.com/watch?v=sVXmwHM06w8&t=4s&ab_channel=KailashSubramaniyam"
    st.video(video_url, loop=False, autoplay=True, muted=False)

c1,c2,c3 = st.columns(3)
with c2:
    if st.button('How to use this APP'):
        show_video()
        
latitude, longitude = 51.5074456, -0.1277653 # London
if 'latitude' not in st.session_state:
    st.session_state.latitude = latitude
if 'longitude' not in st.session_state:
    st.session_state.longitude = longitude

uploaded_file = st.file_uploader("Start by uploading an image...", type=['png', 'jpg', 'jpeg', 'webp', 'heic'])

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
    st.success(f'AI Classification : {category}')

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
            address = st.text_input("Enter your POSTCODE or street name or city:")
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
                    sanitized_comment = comment.replace(',', '')
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
        <h3>INTERACTIVE LIVE MAP</h3>
    </div>
    <div class="centered">
        <i>Hover over the markers for details<i>
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

st.markdown("""
    <style>
    .centered-buttons {
        display: flex;
        justify-content: center;
        gap: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# Container to center the buttons
st.markdown('<div class="centered-buttons">', unsafe_allow_html=True)

st.markdown("""
    <div class="centered-buttons">
        <a href="https://litapp.streamlit.app/Graph_View" target="_self"><button>Trends</button></a>
        <a href="https://litapp.streamlit.app/Map_View" target="_self"><button>Maps</button></a>
        <a href="https://litapp.streamlit.app/Summary" target="_self"><button>Summary</button></a>
    </div>
    """, unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

st.markdown("""
<div style='text-align: center;'>
    Built by <a href="https://kailashsubramaniyam.com/">Kai</a>. Like this? <a href="https://kailashsubramaniyam.com/contact">Hire me!</a>
</div>
""", unsafe_allow_html=True)
