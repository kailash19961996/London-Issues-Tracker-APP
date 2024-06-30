import streamlit as st
import os
from datetime import datetime
from PIL import Image
from transformers import CLIPProcessor, CLIPModel
import torch
import openai
import requests
import pandas as pd

# Initialize the CLIP model and processor
model = CLIPModel.from_pretrained('openai/clip-vit-base-patch32')
processor = CLIPProcessor.from_pretrained('openai/clip-vit-base-patch32')

# Set OpenAI API key
api_key = os.getenv('OPENAI_API_KEY')
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
csv_path = "REPORTED_DATA.csv"
if not os.path.exists(csv_path):
    with open(csv_path, 'w') as f:
        f.write("timestamp,latitude,longitude,category,image_path,comment\n")

# Function to classify image
def classify_image(image):
    inputs = processor(text=categories, images=image, return_tensors="pt", padding=True)
    outputs = model(**inputs)
    logits_per_image = outputs.logits_per_image
    probs = logits_per_image.softmax(dim=1)
    category_index = probs.argmax().item()
    return categories[category_index]

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

# Streamlit UI
st.subheader('🏡 What\'s happening in my Neighbourhood 📝')

# File uploader
uploaded_file = st.file_uploader("Choose an image...", type=['png', 'jpg', 'jpeg'])
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
    st.success(f'Classified as {category}')
    
# Text box for comments
comment = st.text_input("Add a comment about the image:")
if st.button('Submit Comment'):
    # Get the timestamp
    timestamp = datetime.now()
    # Get and save the user's location
    latitude, longitude = get_user_location()
    if comment:
        # Remove all commas from the comment
        sanitized_comment = comment.replace(',', '')
        # Save the image
        image.save(image_path)
        # save all the info it to CSV
        save_image_data(timestamp, latitude, longitude, image_path, category, sanitized_comment)
        st.success('Comment added successfully and data saved!')
    else:
        st.error('Please add a comment before submitting.')
