import streamlit as st
import google.generativeai as genai
import os
from dotenv import load_dotenv
load_dotenv()  # Loading all the environment variables
from PIL import Image
import requests

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
st.set_page_config(page_title="Gemini Calorie Tracker", page_icon="🍏")
# Title and header with user information
st.title("Gemini Calorie Tracker")

# User information to create a user using the Flask API /create_user
st.header("User Information")
user_name = st.text_input("Enter your name:")
user_email = st.text_input("Enter your email:")
submit_user = st.button("Submit", key=1)

if submit_user:
    user_data = {"user_name": user_name, "user_email": user_email}
    resp = requests.post(f"{FLASK_SERVER_URL}/create_user", json=user_data)

    # Store user_email in session
    st.session_state.user_email = resp.json().get("user_email")

    st.success(f"Logged in as User: {st.session_state.user_email}")
    logout_button = st.button("Logout")

    if logout_button:
        # Remove user_id from session
        del st.session_state.user_email
        st.success("Logged out successfully!")

    # get user information from database get /user_info
    if st.session_state.user_email:
        user_info = requests.get(f"{FLASK_SERVER_URL}/user_info/{st.session_state.user_email}")

        # Display user information as a table
        st.header("User Information")
        # columnsnames in table
        print(user_info.json().get("user_info"))
        st.table([["ID","Name","Email","Calories"],user_info.json().get("user_info")])
        
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
    If you are done with the above, please enter the total calories of the food item like *Total calories: 1000
    """

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

        user_data = {"user_name": user_name, "user_email": user_email, "calories": calories}
        response_server = requests.post(f"{FLASK_SERVER_URL}/store_calories", json=user_data)
        st.header("Response")
        st.write(resp)

# Follow-up conversation with AI
follow_up_query = st.text_input("Continue the conversation:")
follow_up_submit = st.button("Submit", key=3)

if follow_up_submit:
    follow_up_resp = get_gemini_resp(prompt=follow_up_query, image=input_image_setup(upload_file))
    st.header("Follow-up Response")
    st.write(follow_up_resp)
