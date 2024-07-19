import base64
import time
import streamlit as st
from opencage.geocoder import OpenCageGeocode
from io import BytesIO
import openai
import os

# OpenAI API key
api_key = st.secrets["openai"]["api_key"]
if api_key is None:
    raise ValueError("API key not found. Please set the OPENAI_API_KEY environment variable.")
openai.api_key = api_key

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

def get_geolocation(address):
    key = 'e14c2a19f39146c4be104fe2f2289369' 
    geocoder = OpenCageGeocode(key)
    try:
        result = geocoder.geocode(address)
        if result and len(result):
            location = result[0]['geometry']
            area_name = result[0]['formatted']
            return location['lat'], location['lng'], area_name
        else:
            return None, None, None
    except Exception as e:
        st.error(f"Geocoding service error: {e}")
        return None, None, None
    
def classify_image(image):
    # Convert the image to base64
    buffered = BytesIO()
    image.save(buffered, format="PNG")
    image_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
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
    

