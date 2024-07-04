import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st
from datetime import datetime
from background import add_bg_from_local
from Home import api_key
from PIL import Image
import base64
from io import BytesIO

add_bg_from_local('APP/background_images/background.gif')

logo = Image.open("APP/background_images/logo_wihtout_background.png")
buffered = BytesIO()
logo.save(buffered, format="PNG")
logo_base64 = base64.b64encode(buffered.getvalue()).decode()
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
        <h1>Trends by Category</h1>
    </div>
    """, unsafe_allow_html=True)

st.markdown("""
<div style='text-align: center;'>
<i>"Graphical representations track issue trends over time, helping monitor progress and accountability."<i>       
</div>
""", unsafe_allow_html=True)

# Load the provided CSV file
file_path = 'APP/REPORTED_DATA.csv'  # Update this path as necessary
df = pd.read_csv(file_path)

# Clean the timestamp column
df['timestamp'] = df['timestamp'].str.extract(r'(^[\d\-:\s\.]+)').dropna()

# Convert the timestamp column to datetime
df['timestamp'] = pd.to_datetime(df['timestamp'], format='%Y-%m-%d %H:%M:%S', errors='coerce')

# Set timestamp as index
df.set_index('timestamp', inplace=True)

# Select category
categories = df['category'].unique()
selected_category = st.selectbox('Start by Selecting a Category', categories)

# Filter data by selected category
df_filtered = df[df['category'] == selected_category]

# Resample by week to count comments
comments_per_week = df_filtered['comment'].resample('W').count()

# Resample by month to count comments
comments_per_month = df_filtered['comment'].resample('ME').count()

# Apply a style
plt.style.use('Solarize_Light2')

# Create two columns for side-by-side plots
col1, col2 = st.columns(2)

with col1:
    st.subheader(f'Comments per Week ({selected_category})')
    fig_week, ax_week = plt.subplots(figsize=(5, 3))
    ax_week.plot(comments_per_week.index, comments_per_week, marker='o', color='teal', label='Comments per Week')
    ax_week.set_ylabel('Number of Comments')
    ax_week.grid(True)
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    st.pyplot(fig_week)

with col2:
    st.subheader(f'Comments per Month ({selected_category})')
    fig_month, ax_month = plt.subplots(figsize=(5, 3))
    ax_month.plot(comments_per_month.index, comments_per_month, marker='o', color='darkred', label='Comments per Month')
    ax_month.set_ylabel('Number of Comments')
    ax_month.grid(True)
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    st.pyplot(fig_month)

# Display the raw data
st.markdown("""
<div style='text-align: center;'>
    <h2> User Reports </h2>
</div>
""", unsafe_allow_html=True)
st.write(df_filtered)

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

# Buttons with links
st.markdown("""
    <div class="centered-buttons">
        <a href="https://litapp.streamlit.app" target="_self"><button>Go to Home</button></a>
        <a href="https://litapp.streamlit.app/Map_View" target="_self"><button>Go to Maps</button></a>
        <a href="https://litapp.streamlit.app/Summary" target="_self"><button>Go to Summary</button></a>
        <a href="https://kailashsubramaniyam.com/" target="_self"><button>Reach out to me</button></a>
    </div>
    """, unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)
