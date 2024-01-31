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
    st.write(resp.json())

upload_file = st.file_uploader("Choose an image : ", type=['jpg','png','jpeg'])
image=""

if upload_file is not None:
    image = Image.open(upload_file)
    st.image(image, caption="Upload image ",use_column_width=True)

input_query = st.text_input("Run below? or enter a manual query ")

submit = st.button("Submit", key=2)


input_prompt="""
    You are an expert in nutritionist where you need to see the food items from the image and calculate the total calories, also provide the details of every food items with calories intake in below format
    
    Describe the meal: 
    
    1. Item 1 no of calories

    2. Item 2 no of calories
    
    and also mention the percentage split of the ratio of carbohydrates, fats, fibers, sugar and other things required in our diet 
    Finally you can also mention whether the food is healthy or not!
    """

if submit:
    image_data = input_image_setup(upload_file)
    resp = None

    if input_query != "":
        resp = get_gemini_resp( prompt=input_query, image=image_data)
    else:
        resp = get_gemini_resp( prompt=input_prompt, image=image_data)

    calories = get_gemini_resp( prompt="Type just calories below if it is food, else 0 : ", image=image_data)

    user_data = {
        "user_name":user_name,
        "user_email":user_email,
        "calories":calories
    }
    response_server = requests.post(f"{FLASK_SERVER_URL}/store_calories", json=user_data)
    st.write(response_server.json())
    st.header("Yes, \n")
    st.write(resp)