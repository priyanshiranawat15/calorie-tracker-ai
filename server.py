from flask import Flask, request, jsonify, render_template, session, redirect, url_for
import psycopg2
from dotenv import load_dotenv
import os
import hashlib
from flask_cors import CORS

load_dotenv()  # Load environment variables

app = Flask(__name__)
CORS(app)
app.secret_key = os.getenv("SECRET_KEY")

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
            user_name = request.form.get("name")
            user_email = request.form.get("email")
            print(user_email)
            user_password = request.form.get("password")
            print(user_password)
            # safely store the password in the database
            user_password = hashlib.sha256(user_password.encode()).hexdigest()

            # Store the data in the database
            with get_db_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        #deal with the conflict if the user already exists
                        f"INSERT INTO users (user_name, user_email, password) VALUES ('{str(user_name)}','{str(user_email)}', '{str(user_password)}') ON CONFLICT (user_email) DO NOTHING"
                    )
                    conn.commit()
            print(jsonify({"success": True, "message": "User created successfully", "user_email": user_email}))
            return redirect(url_for("login"))
        except Exception as e:
            print(e)
            return jsonify({"success": False, "error": str(e)})
        
    return render_template("register.html")
        
# Endpoint to authenticate user
@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        try:
            user_email = request.form.get("email")
            user_password = request.form.get("password")

            # safely store the password in the database
            user_password = hashlib.sha256(user_password.encode()).hexdigest()

            # Store the data in the database
            with get_db_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        f"SELECT * FROM users WHERE user_email LIKE '{user_email}' AND password LIKE '{user_password}'"
                    )
                    user_info = cur.fetchone()

            if user_info:
                # save the user info in the session
                session["user_info"] = user_info

                print(jsonify({"success": True, "message": "User authenticated successfully", "user_info": user_info}))
                return redirect(url_for("home"))
            else:
                return jsonify({"success": False, "message": "User authentication failed"})
        except Exception as e:
            print(e)
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

@app.route("/", methods=["GET"])
def home():
    # check if already logged in
    if "user_info" not in session:
        return redirect(url_for("login"))
    
    # if not logged in, redirect to login page

    return render_template("index.html")  

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
    app.run(host='0.0.0.0', port=5000, debug=True)