import base64
import time
import streamlit as st
from geopy.geocoders import Nominatim

def add_bg_from_local(image_file):
    with open(image_file, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read())
    st.markdown(
    f"""
    <style>
    .stApp {{
        background-image: url(data:image/{"jpg"};base64,{encoded_string.decode()});
        background-size: cover
    }}
    </style>
    """,
    unsafe_allow_html=True
    )

def show_gif_overlay(gif_path, duration):
    gif_html = f"""
        <style>
        .gif-overlay {{
            position: fixed;
            top: 75%;
            left: 50%;
            transform: translate(-50%, -50%);
            z-index: 9999;
        }}
        </style>
        <div class="gif-overlay">
            <img src="data:image/gif;base64,{base64.b64encode(open(gif_path, "rb").read()).decode()}" alt="Overlay GIF">
        </div>
    """
    overlay_placeholder = st.empty()
    overlay_placeholder.markdown(gif_html, unsafe_allow_html=True)
    time.sleep(duration)
    overlay_placeholder.empty()

# Function to get geolocation data
def get_geolocation(address):
    geolocator = Nominatim(user_agent="geoapiExercises")
    location = geolocator.geocode(address)
    if location:
        return location.latitude, location.longitude
    else:
        return None, None
