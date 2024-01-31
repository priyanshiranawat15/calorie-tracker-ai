from flask import Flask, request, jsonify
import psycopg2
from dotenv import load_dotenv
import os

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
@app.route("/create_user", methods=["POST"])
def create_user():
    try:
        data = request.get_json()
        user_name = data.get("user_name")
        user_email = data.get("user_email")

        # Store the data in the database
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    #deal with the conflict if the user already exists
                    f"INSERT INTO users (user_name, user_email) VALUES ('{str(user_name)}', '{str(user_email)}') ON CONFLICT (user_email) DO NOTHING"
                )
                conn.commit()

        return jsonify({"success": True, "message": "User created successfully"})
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
                    "INSERT INTO users (user_name, user_email, calories) VALUES (%s, %s, %s) ON CONFLICT (user_email) DO UPDATE SET calories = %s",
                    (user_name, user_email, calories, calories)
                    )
                conn.commit()

        return jsonify({"success": True, "message": "Calories stored successfully"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})
    
if __name__ == "__main__":
    app.run(debug=True)