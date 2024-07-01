import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st
from datetime import datetime
from background import add_bg_from_local

add_bg_from_local('APP/background_images/background.gif')

# Streamlit app
st.title('Comments Over Time by Category')

# Load the provided CSV file
file_path = 'REPORTED_DATA.csv'  # Update this path as necessary
df = pd.read_csv(file_path)

# Clean the timestamp column
df['timestamp'] = df['timestamp'].str.extract(r'(^[\d\-:\s\.]+)').dropna()

# Convert the timestamp column to datetime
df['timestamp'] = pd.to_datetime(df['timestamp'], format='%Y-%m-%d %H:%M:%S', errors='coerce')

# Set timestamp as index
df.set_index('timestamp', inplace=True)

# Select category
categories = df['category'].unique()
selected_category = st.selectbox('Select Category', categories)

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
