import streamlit as st
import google.generativeai as genai
import os
from dotenv import load_dotenv
load_dotenv()  # Loading all the environment variables
from PIL import Image
import requests
from server import get_db_connection
import pandas as pd
import plotly.express as px

# Set the FLASK_SERVER_URL
FLASK_SERVER_URL = os.getenv("FLASK_SERVER_URL")

# Configure generativeai
genai.configure(api_key=os.getenv("API_KEY"))

# Function to get Gemini response
def get_gemini_resp(prompt, image):
    model = genai.GenerativeModel('gemini-pro-vision')
    resp = model.generate_content([prompt, image[0]])

    return resp.text

# Function to set up image data
def input_image_setup(uploaded_file):
    print(type(uploaded_file))
    if uploaded_file is not None:
        bytes_data = uploaded_file.getvalue()

        image_data = [
            {
                "mime_type": uploaded_file.type,
                "data": bytes_data
            }
        ]
        return image_data
    else:
        raise FileNotFoundError("No file found")

# Set Streamlit page configuration
st.set_page_config(page_title="Track My Calorie", page_icon="🍏")
# Title and header with user information
st.title("Gemini Calorie Tracker")

        
# File uploader for image
upload_file = st.file_uploader("Choose an image:", type=['jpg', 'png', 'jpeg'])
image = ""

# Display uploaded image
if upload_file is not None:
    image = Image.open(upload_file)
    st.image(image, caption="Upload image", use_column_width=True)

# Text input for query and submission button
input_query = st.text_input("Run below or enter a manual query:")
submit_query = st.button("Submit", key=2)

# Prompt text
input_prompt = """
    If the picture doesn't contain food items, just write *Total calories: 0
    You are an expert in nutritionist where you need to see the food items from the image and calculate the total calories, also provide the details of every food items with calories intake in below format
    
    Describe the meal: 
    
    1. Item 1 no of calories

    2. Item 2 no of calories
    
    and also mention the percentage split of the ratio of carbohydrates, fats, fibers, sugar and other things required in our diet 
    Finally you can also mention whether the food is healthy or not!
    If you are done with the above, please enter the total calories of the food item like *Total calories: 1000 (just the number as it is directly stored in database as an integer) in the end
    """

def visualize():
    conn = get_db_connection()
    avg_per_day_df = pd.read_sql_query(
        """SELECT to_char(time_stamp, 'YYYY-MM-DD') AS date,
            AVG(calories) AS average_calories
        FROM calories
        GROUP BY date;""",
        conn
    )

    avg_per_weekday_df = pd.read_sql_query(
        """
        SELECT EXTRACT(DOW FROM time_stamp) AS day_of_week, 
            AVG(calories) AS average_calories 
        FROM calories 
        GROUP BY day_of_week;
        """,
        conn
    )
    conn.close()

    return avg_per_day_df, avg_per_weekday_df


# Process query and display response
if submit_query:
    with st.spinner('Generating response...'):
        image_data = input_image_setup(upload_file)
        resp = None

        if input_query != "":
            resp = get_gemini_resp(prompt=input_query + "\nIf you are done with the above, please enter the total calories of the food item like *Total calories: 1000", image=image_data)
        else:
            resp = get_gemini_resp(prompt=input_prompt, image=image_data)

        calories = resp.split("Total calories:")[1].split("\n")[0]
        print(calories)

        user_data = {"user_email": 'd@gmail.com', "calories": calories}
        response_server = requests.post(f"{FLASK_SERVER_URL}/store_calories", json=user_data)
        st.write(response_server.json())
        st.header("Response")
        st.write(resp)

# Follow-up conversation with AI
follow_up_query = st.text_input("Continue the conversation:")
follow_up_submit = st.button("Submit", key=3)

# sidebar to display stats of calories per day, per week and per month
avg_per_day_df, avg_per_weekday_df = visualize()

st.sidebar.title("Calories Stats")
st.sidebar.header("Average Calories per Day")
st.sidebar.line_chart(avg_per_day_df, x='date', y='average_calories')

st.sidebar.header("Average Calories per Day of Week")
# Replace with a suitable visualization (bar chart?)
fig = px.bar(avg_per_weekday_df, x='day_of_week', y='average_calories') 

# Display in Streamlit
st.sidebar.plotly_chart(fig)   


if follow_up_submit:
    follow_up_resp = get_gemini_resp(prompt=follow_up_query, image=input_image_setup(upload_file))
    st.header("Follow-up Response")
    st.write(follow_up_resp)
