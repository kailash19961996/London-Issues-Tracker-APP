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
from background import add_bg_from_local, show_gif_overlay

add_bg_from_local('APP/background_images/whitebgs.jpg')

logo = Image.open("APP/background_images/logo_wihtout_background.png")

# Create columns to align the logo left of the title
col1, col2 = st.columns([1, 5])

with col1:
    st.image(logo, width=100)  # Adjust width as needed
with col2:
    st.markdown("""
    <div style='text-align: center;'>
    <h1> < London Issue Tracker > </h1>
    </div>
    """, unsafe_allow_html=True)
    st.title("London Issue Tracker")

st.markdown("""
<div style='text-align: center;'>
    <h4> < POWERED BY AI > </h4>
</div>
""", unsafe_allow_html=True)

# File uploader
uploaded_file = st.file_uploader("Choose an image...", type=['png', 'jpg', 'jpeg', 'webp', 'heic'])

# Set OpenAI API key
api_key = st.secrets["openai"]["api_key"]
if api_key is None:
    raise ValueError("API key not found. Please set the OPENAI_API_KEY environment variable.")
openai.api_key = api_key

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

# Function to classify image
def classify_image(image):
    # Convert the image to base64
    buffered = BytesIO()
    image.save(buffered, format="PNG")
    image_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Classify this image mostly into one of the following categories: graffiti, garbage, broken_window, green_spaces, public_buildings, sports_and_social_events, other. Respond with only the category name."},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{image_base64}"
                            }
                        }
                    ]
                }
            ],
            max_tokens=10
        )
        return response.choices[0].message.content.strip().lower()
    except Exception as e:
        st.error(f"Error classifying image: {str(e)}")
        return None
    

# Function to get user's location based on IP address
def get_user_location():
    response = requests.get("https://ipinfo.io")
    data = response.json()
    location = data['loc'].split(',')
    latitude = float(location[0])
    longitude = float(location[1])
    return latitude, longitude

# Function to save image data to CSV
def save_image_data(timestamp, latitude, longitude, image_path, category, comment):
    with open(csv_path, 'a') as f:
        f.write(f"{timestamp},{latitude},{longitude},{category},{image_path},{comment}\n")

w_size = 250
h_size = 250

if uploaded_file is not None:
    image = Image.open(uploaded_file)

    # Resize the image to half its original size
    original_size = image.size
    new_size = (int(w_size), int(h_size))
    resized_image = image.resize(new_size)

    # Display the resized image
    st.image(resized_image, caption='Uploaded Image.', use_column_width=False)

    # Classify  the image
    category = classify_image(image)          
    image_path = os.path.join(images_dir, uploaded_file.name)
    st.success(f'Classification : {category}')
    if category not in categories:
        # Sample image download button
        sample_image_path = 'APP/sample_image/graffiti.jpg'  # Path to your sample image
        if os.path.exists(sample_image_path):
            with open(sample_image_path, "rb") as file:
                st.markdown("""
                    <div style='text-align: center;'>
                    - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
                    </div>
                    """, unsafe_allow_html=True)
                
                st.write(f"NOTE : As of now, the model is designed to detect only these 6 categories: ")
                st.write(f"Graffiti, Garbage, Broken Window, Green Spaces, Public Buildings, Sports and Social events")
                st.write(f"Read the documentation on Github repo for more info. If you are not sure what to upload, download the sample image below.")
                st.markdown("""
                    <div style='text-align: center;'>
                    - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
                    </div>
                    """, unsafe_allow_html=True)
                btn = st.download_button(
                    label="Download a sample image",
                    data=file,
                    file_name="sample.jpg",
                    mime="image/jpeg")
    else:
        # Text box for comments
        comment = st.text_input("Add a comment about the image:")

        if st.button('Submit Comment'):
            show_gif_overlay('APP/background_images/stars.gif', duration=8)
            # Get the timestamp
            timestamp = datetime.now()
            formatted_timestamp = timestamp.strftime('%Y-%m-%d %H:%M:%S')

            # Get and save the user's location
            latitude, longitude = get_user_location()
            st.write(f"Your location is: Latitude: {latitude}, Longitude: {longitude}")
            if comment:
                # Remove all commas from the comment
                sanitized_comment = comment.replace(',', '')
                # Save the image
                image.save(image_path)
                # save all the info it to CSV
                save_image_data(formatted_timestamp, latitude, longitude, image_path, category, sanitized_comment)
                st.success('Thanks for reporting your thoughts, we will look into it.')
            else:
                st.error('Please add a comment before submitting.')

# Load the data
data = pd.read_csv('APP/REPORTED_DATA.csv', parse_dates=[0])

st.markdown("""
<div style='text-align: center;'>
    <h2>     Interactive Live Map </h2>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div style='text-align: center;'>
Hover over the red spots for more info
</div>
""", unsafe_allow_html=True)

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

view_state = pdk.ViewState(latitude=current_latitude, longitude=current_longitude, zoom=12)
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
st.write(f"NOTE: The location is identified based on the IP address, since streamlit servers are located at Dalles, Oregon, United States, you will find the current location to be wrong.")
st.markdown("""
<div style='text-align: center;'>
- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
</div>
""", unsafe_allow_html=True)
