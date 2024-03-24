from flask import Flask, request, jsonify, render_template
import psycopg2
from dotenv import load_dotenv
import os
import hashlib

load_dotenv()  # Load environment variables

app = Flask(__name__)

# Database connection parameters
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

# Define the database connection function
def get_db_connection():
    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
    )

# Endpoint to create user in database
@app.route("/register", methods=["GET","POST"])
def register():
    if request.method == "POST":
        try:
            data = request.get_json()
            user_email = data.get("user_email")
            user_password = data.get("user_password")

            # safely store the password in the database
            user_password = hashlib.sha256(user_password.encode()).hexdigest()

            # Store the data in the database
            with get_db_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        #deal with the conflict if the user already exists
                        f"INSERT INTO users (user_email, user_password) VALUES ('{str(user_email)}', '{str(user_password)}') ON CONFLICT (user_email) DO NOTHING"
                    )
                    conn.commit()
            return jsonify({"success": True, "message": "User created successfully", "user_email": user_email})
        except Exception as e:
            return jsonify({"success": False, "error": str(e)})
        
    return render_template("register.html")
        
# Endpoint to authenticate user
@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        try:
            data = request.get_json()
            user_email = data.get("user_email")
            user_password = data.get("user_password")

            # safely store the password in the database
            user_password = hashlib.sha256(user_password.encode()).hexdigest()

            # Store the data in the database
            with get_db_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        f"SELECT * FROM users WHERE user_email LIKE '{user_email}' AND user_password LIKE '{user_password}'"
                    )
                    user_info = cur.fetchone()

            if user_info:
                return jsonify({"success": True, "message": "User authenticated successfully", "user_info": user_info})
            else:
                return jsonify({"success": False, "message": "User authentication failed"})
        except Exception as e:
            return jsonify({"success": False, "error": str(e)})
        
    return render_template("login.html")

# Endpoint to get user information from database
@app.route("/user_info/<user_email>", methods=["GET"])
def user_info(user_email):
    try:
        # Store the data in the database
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    f"SELECT * FROM users WHERE user_email LIKE '{user_email}'"
                )
                user_info = cur.fetchone()

        return jsonify({"success": True, "message": "User information retrieved successfully", "user_info": user_info})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})
    

# Endpoint to store calories of user and update if already exists
@app.route("/store_calories", methods=["POST"])
def store_calories():
    try:
        data = request.get_json()
        user_email = data.get("user_email")
        user_name = data.get("user_name")
        calories = data.get("calories")

        # Store the data in the database
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    #deal with the conflict if the user already exists
                    "INSERT INTO calories (user_email, calories) VALUES (%s, %s) ",
                    (user_email, calories)
                    )
                conn.commit()

        return jsonify({"success": True, "message": "Calories stored successfully"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})
    
if __name__ == "__main__":
    app.run(debug=True)