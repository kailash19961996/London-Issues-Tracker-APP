import streamlit as st
import pandas as pd
import openai
import os

# Set OpenAI API key
api_key = os.getenv('OPENAI_API_KEY')
if api_key is None:
    raise ValueError("API key not found. Please set the OPENAI_API_KEY environment variable.")
openai.api_key = api_key

# Load the provided CSV file
file_path = 'REPORTED_DATA.csv'  # Update this path as necessary
df = pd.read_csv(file_path)

# Convert the timestamp column to datetime
df['timestamp'] = pd.to_datetime(df['timestamp'])

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
                model="gpt-4",
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

# Streamlit app
st.title('Summarize Comments by Category')

# Display the raw data
st.subheader('Raw Data')
st.write(df)

# Summarize comments
if st.button('Summarize Comments'):
    summaries = summarize_comments(df)
    st.markdown(summaries)
