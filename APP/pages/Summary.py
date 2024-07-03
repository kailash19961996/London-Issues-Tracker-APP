import streamlit as st
import pandas as pd
import openai
import os
from background import add_bg_from_local, show_gif_overlay
from Home import api_key

add_bg_from_local('APP/background_images/whitebgs.jpg')

openai.api_key = api_key

# Load the provided CSV file
file_path = 'APP/REPORTED_DATA.csv'
df = pd.read_csv(file_path)
df['timestamp'] = df['timestamp'].str.extract(r'(^[\d\-:\s\.]+)').dropna()
df['timestamp'] = pd.to_datetime(df['timestamp'], format='%Y-%m-%d %H:%M:%S', errors='coerce')
df.set_index('timestamp', inplace=True)

# Function to summarize comments
def summarize_comments(df):
    summaries = []
    feedback_counts = []
    categories = df['category'].unique()
    for category in categories:
        df_category = df[df['category'] == category]
        
        # Count number of feedbacks (images) in the category
        feedback_count = df_category.shape[0]
        feedback_counts.append((category, feedback_count))
        
        comments = " ".join(df_category['comment'].tolist())
        if comments:
            prompt = f"Summarize the following user comments and address the major concerns mentioned:\n\n{comments}"
            response = openai.ChatCompletion.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=2000,
                temperature=0.5
            )
            summary = response.choices[0].message['content'].strip()
            summaries.append((category, summary))
    
    # Sort summaries based on feedback count from highest to lowest
    feedback_counts.sort(key=lambda x: x[1], reverse=True)
    
    summary_text = ""
    for category, count in feedback_counts:
        summary_text += f"**{category}** - {count} feedback(s)\n"
        summary_text += next((summary for cat, summary in summaries if cat == category), "No summary available") + "\n\n"
    
    return summary_text

st.markdown("""
<div style='text-align: center;'>
    <h1> Summary by Category </h1>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div style='text-align: center;'>
"The AI summary feature is incredibly helpful when there are thousands of comments, as it generates concise overviews, making it easier to quickly grasp the key issues and insights."        
</div>
""", unsafe_allow_html=True)


# Summarize comments
if st.button('Summarize Comments'):
    summaries = summarize_comments(df)
    st.markdown(summaries)
    show_gif_overlay('APP/background_images/stars2.gif', duration=5)

# Display the dataframe to inspect the columns
st.markdown("""
<div style='text-align: center;'>
    <h2> User Reports </h2>
</div>
""", unsafe_allow_html=True)
st.write(df)

# Create an expander for project information
with st.expander("About the Project"):
    st.markdown("""
    # Welcome to Our Project
The London Issues Tracker is a groundbreaking platform developed during the Future House hackathon, designed to engage community members and policymakers in addressing urban challenges. Leveraging advanced AI, the platform efficiently processes and analyzes user-submitted reports, providing valuable insights into local issues. Users can upload images and comments about urban problems, which are displayed in real-time on interactive maps. These maps allow both users and policymakers to visualize reported issues and take necessary actions.

Key features include AI-generated summaries of user comments, making it easier to understand large volumes of feedback, and graphical representations of issue trends over time, aiding in tracking progress and accountability. The platform aims to enhance urban aesthetics, improve community well-being, promote sustainability, and ensure public safety. Future development ideas include sentiment analysis, predictive modeling, and chatbot integration to further enhance user engagement and functionality. The London Issues Tracker is a powerful tool for fostering community involvement and informed decision-making in urban management.
    """)
