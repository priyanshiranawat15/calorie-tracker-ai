import streamlit as st
import google.generativeai as genai
import os
from dotenv import load_dotenv
load_dotenv() #loading all the environment variables
from PIL import Image
import requests


FLASK_SERVER_URL = os.getenv("FLASK_SERVER_URL")


genai.configure(api_key=os.getenv("API_KEY"))

def get_gemini_resp(prompt, image):
    model = genai.GenerativeModel('gemini-pro-vision')
    resp = model.generate_content([prompt, image[0]])

    return resp.text

def input_image_setup(uploaded_file):
    if uploaded_file is not None:
        bytes_data = uploaded_file.getvalue()

        image_data = [
            {
                "mime_type":uploaded_file.type,
                "data":bytes_data
            }
        ]
        return image_data
    
    else:
        raise FileNotFoundError("No file found")
    


st.set_page_config(page_title="Gemeni calorie tracker")

st.title("Gemini Calorie Tracker")

#user information to create user using flask api /create_user
st.header("User Information")
user_name = st.text_input("Enter your name : ")
user_email = st.text_input("Enter your email : ")
submit_user = st.button("Submit", key=1)

if submit_user:
    user_data = {
        "user_name":user_name,
        "user_email":user_email
    }
    resp = requests.post(f"{FLASK_SERVER_URL}/create_user", json=user_data)

    # store user_email in session
    st.session_state.user_email = resp.json().get("user_email")

    # st.write(resp.json())


    st.success(f"Logged in as User: {st.session_state.user_email}")
    logout_button = st.button("Logout")

    if logout_button:
        # Remove user_id from session
        del st.session_state.user_email
        st.success("Logged out successfully!")

upload_file = st.file_uploader("Choose an image : ", type=['jpg','png','jpeg'])
image=""

if upload_file is not None:
    image = Image.open(upload_file)
    st.image(image, caption="Upload image ",use_column_width=True)

input_query = st.text_input("Run below or enter a manual query ")

submit_query = st.button("Submit", key=2)


input_prompt="""
    If the picture doesn't contain food items, just write *Total calories: 0
    You are an expert in nutritionist where you need to see the food items from the image and calculate the total calories, also provide the details of every food items with calories intake in below format
    
    Describe the meal: 
    
    1. Item 1 no of calories

    2. Item 2 no of calories
    
    and also mention the percentage split of the ratio of carbohydrates, fats, fibers, sugar and other things required in our diet 
    Finally you can also mention whether the food is healthy or not!
    If you are done with the above, please enter the total calories of the food item like *Total calories: 1000
    """
im_data = None
if submit_query:
    image_data = input_image_setup(upload_file)
    resp = None

    if input_query != "":
        resp = get_gemini_resp( prompt=input_query + "\nIf you are done with the above, please enter the total calories of the food item like *Total calories: 1000", image=image_data)
    else:
        resp = get_gemini_resp( prompt=input_prompt, image=image_data)

    calories = resp.split("Total calories:")[1].split("\n")[0]

    user_data = {
        "user_name":user_name,
        "user_email":user_email,
        "calories":calories
    }
    response_server = requests.post(f"{FLASK_SERVER_URL}/store_calories", json=user_data)
    # st.write(response_server.json())
    st.header("Response, \n")
    st.write(resp) 

# Follow-up conversation with AI
follow_up_query = st.text_input("Continue the conversation:")
follow_up_submit = st.button("Submit", key=3)

if follow_up_submit:
    follow_up_resp = get_gemini_resp(prompt=follow_up_query, image=input_image_setup(upload_file))
    st.header("Follow-up Response, \n")
    st.write(follow_up_resp)