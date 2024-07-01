import streamlit as st
import pandas as pd
import openai
import os
from background import add_bg_from_local

add_bg_from_local('background_images/whitebgs.jpg')

# Set OpenAI API key
api_key = os.getenv('OPENAI_API_KEY')
if api_key is None:
    raise ValueError("API key not found. Please set the OPENAI_API_KEY environment variable.")
openai.api_key = api_key

# Set OpenAI API key
api_key = os.getenv('OPENAI_API_KEY')
if api_key is None:
    raise ValueError("API key not found. Please set the OPENAI_API_KEY environment variable.")
openai.api_key = api_key

# Load the provided CSV file
file_path = 'REPORTED_DATA.csv'  # Update this path as necessary
df = pd.read_csv(file_path)

# Clean the timestamp column
df['timestamp'] = df['timestamp'].str.extract(r'(^[\d\-:\s\.]+)').dropna()

# Convert the timestamp column to datetime
df['timestamp'] = pd.to_datetime(df['timestamp'], format='%Y-%m-%d %H:%M:%S', errors='coerce')

# Set timestamp as index
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

st.write(f"Use Latest and powerful LLM's like GPT-4o to summarize this report")
# Summarize comments
if st.button('Summarize Comments'):
    summaries = summarize_comments(df)
    st.markdown(summaries)

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

    This project focuses on several key areas in urban environments:

    - **GRAFFITI**: Exploring the artistic and social impacts of graffiti in cities.
    - **GARBAGE**: Addressing waste management and cleanliness in urban areas.
    - **BROKEN WINDOWS**: Studying the effects of urban decay and vandalism.
    - **GREEN SPACES**: Promoting parks and natural areas for community well-being.
    - **PUBLIC BUILDINGS**: Evaluating the use and maintenance of public infrastructure.
    - **SPORTS AND SOCIAL EVENTS**: Encouraging physical activities, social gatherings and events in neighborhoods.

    ## Objectives

    - **Urban Aesthetics**: Enhancing the visual appeal of urban environments.
    - **Community Health**: Improving the overall health and well-being of residents.
    - **Sustainability**: Promoting sustainable practices in waste management and green spaces.
    - **Safety**: Ensuring safe and welcoming public spaces.

    ## How You Can Get Involved

    We welcome community participation and input. Here are a few ways you can contribute:

    - **Active sharing**
    - **Verifying others report**
    - **Keeping the authorities accountable**

    Thank you for visiting our project page. Together, we can make our cities better places to live.
    """)
