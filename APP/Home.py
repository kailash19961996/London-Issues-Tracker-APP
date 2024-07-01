import streamlit as st
import os
from datetime import datetime
from PIL import Image
import openai
import requests
import pandas as pd
import base64
from io import BytesIO
from background import add_bg_from_local

add_bg_from_local('APP/background_images/whitebgs.jpg')

st.markdown("""
<div style='text-align: center;'>
    <h2>🏠 What's happening in Neighbourhood ⛯</h2>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div style='text-align: center;'>
    <h4> < POWERED BY AI > </h4>
</div>
""", unsafe_allow_html=True)



# File uploader
uploaded_file = st.file_uploader("Choose an image...", type=['png', 'jpg', 'jpeg'])

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
    st.write(f"Your location is: Latitude: {latitude}, Longitude: {longitude}")
    return latitude, longitude

# Function to save image data to CSV
def save_image_data(timestamp, latitude, longitude, image_path, category, comment):
    with open(csv_path, 'a') as f:
        f.write(f"{timestamp},{latitude},{longitude},{category},{image_path},{comment}\n")

if uploaded_file is not None:
    image = Image.open(uploaded_file)

    # Resize the image to half its original size
    original_size = image.size
    new_size = (int(original_size[0] / 2), int(original_size[1] / 2))
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
                st.write(f"NOTE : As of now, the model is designed to detect only these 6 categories: ")
                st.write(f"Graffiti, Garbage, Broken Window, Green Spaces, Public Buildings, Sports and Social events")
                st.write(f"If you are not sure what to upload, download the same image below.")
                btn = st.download_button(
                    label="Download a sample image",
                    data=file,
                    file_name="sample.jpg",
                    mime="image/jpeg")
    else:
        # Text box for comments
        comment = st.text_input("Add a comment about the image:")

        if st.button('Submit Comment'):
            # Get the timestamp
            timestamp = datetime.now()
            formatted_timestamp = timestamp.strftime('%Y-%m-%d %H:%M:%S')

            # Get and save the user's location
            latitude, longitude = get_user_location()
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
