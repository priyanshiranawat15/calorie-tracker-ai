from flask import Flask, session, render_template, request, redirect, url_for, flash, jsonify
from flask_cors import CORS
import psycopg2
import os, hashlib, requests, base64, io
from werkzeug.security import generate_password_hash, check_password_hash
import google.generativeai as genai
from dotenv import load_dotenv
load_dotenv()  # Loading all the environment variables
from PIL import Image

app = Flask(__name__)
CORS(app)

# Replace with your PostgreSQL connection string
DATABASE_URL = os.getenv("DATABASE_URL", f'postgresql://{os.getenv("DB_USER")}:{os.getenv("DB_PASSWORD")}@{os.getenv("DB_HOST")}:{os.getenv("DB_PORT")}/{os.getenv("DB_NAME")}')

# Configure generativeai google
genai.configure(api_key=os.getenv("API_KEY"))

# Function to get Gemini response
def get_gemini_resp(prompt, image):
    model = genai.GenerativeModel('gemini-pro-vision')
    resp = model.generate_content([prompt, image[0]])

    return resp.text

prompt = """
    If the picture doesn't contain food items, just write *Total calories: 0
    You are an expert in nutritionist where you need to see the food items from the image and calculate the total calories, also provide the details of every food items with calories intake in below format
    
    Describe the meal: 
    
    1. Item 1 no of calories

    2. Item 2 no of calories
    
    and also mention the percentage split of the ratio of carbohydrates, fats, fibers, sugar and other things required in our diet 
    Finally you can also mention whether the food is healthy or not!
    If you are done with the above, please enter the total calories of the food item like *Total calories: 1000 in the end
    """

def process_image(image_data, prompt):
    try:
        img_data = base64.b64decode(image_data.split(",")[1])
        
        print(type(img_data))
        img = Image.open(io.BytesIO(img_data))

        resp = get_gemini_resp(prompt=prompt, image=img_data)
        calories = resp.split("Total calories:")[1].split("\n")[0]

        return {"response": resp, "calories": calories}

    except Exception as e:
        return {"error": str(e)}

def create_connection():
    return psycopg2.connect(DATABASE_URL)

def execute_query(query, params=None):
    conn = create_connection()
    cur = conn.cursor()

    if params:
        cur.execute(query, params)
    else:
        cur.execute(query)

    conn.commit()
    try:
        result = cur.fetchall()
    except:
        result = None
    cur.close()
    conn.close()

    return result

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['username']
        email = request.form['email']
        password = request.form['password']

        password = password.encode('utf-8')
        hashed_password = hashlib.sha256(password).hexdigest()
        execute_query("INSERT INTO users (user_email, user_name , password) VALUES (%s, %s, %s) ON CONFLICT(user_email) DO NOTHING", (email, name, hashed_password))

        flash('Registration successful. Please log in.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        password = password.encode('utf-8')
        hashed_password = hashlib.sha256(password).hexdigest()
        user = execute_query("SELECT * FROM users WHERE user_email = %s", (email,))

        if user and user[0][-1] == hashed_password:
            flash('Login successful!', 'success')
            # Add user_email to the session
            session['user_email'] = email
            # Here you can add code to create a session or perform other actions upon successful login
            return redirect('/localhost:8501')
        else:
            flash('Invalid username or password. Please try again.', 'error')

    return render_template('login.html')

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/upload_image', methods=['POST'])
def upload_image():
    try:
        image_data = request.files['image']
        print(image_data)
        result = process_image(image_data, prompt)
        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e)})

@app.route("/store_calories", methods=["POST"])
def store_calories():
    try:
        data = request.get_json()
        user_email = data.get("user_email")
        calories = data.get("calories")

        print(user_email)
        print(calories)
        # Store the data in the database
        with create_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    #deal with the conflict if the user already exists
                    "INSERT INTO calories (user_email, calories) VALUES ( %s, %s)",
                    (user_email, calories)
                    )
                conn.commit()

        return jsonify({"success": True, "message": "Calories stored successfully"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})
    

@app.route('/dashboard')
def dashboard():
    return 'Welcome to the Dashboard!'

if __name__ == '__main__':
    app.run(debug=True)
