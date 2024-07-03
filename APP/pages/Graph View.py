import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st
from datetime import datetime
from background import add_bg_from_local
from Home import api_key
from PIL import Image

add_bg_from_local('APP/background_images/background.gif')

logo = Image.open("APP/background_images/logo_wihtout_background.png")

# Create columns to align the logo left of the title
col1, col2 = st.columns([1, 5])
with col1:
    st.image(logo, width=100)
with col2:
    st.title("Trends by Category")

st.markdown("""
<div style='text-align: center;'>
"Graphical representations track issue trends over time, helping monitor progress and accountability."        
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
