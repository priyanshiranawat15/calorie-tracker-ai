from flask import Flask, session, render_template, request, redirect, url_for, flash, jsonify
import psycopg2
import os, hashlib
from werkzeug.security import generate_password_hash, check_password_hash


app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'

# Replace with your PostgreSQL connection string
DATABASE_URL = os.getenv("DATABASE_URL", f'postgresql://{os.getenv("DB_USER")}:{os.getenv("DB_PASSWORD")}@{os.getenv("DB_HOST")}:{os.getenv("DB_PORT")}/{os.getenv("DB_NAME")}')

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
        email = request.form['email']
        password = request.form['password']

        password = password.encode('utf-8')
        hashed_password = hashlib.sha256(password).hexdigest()
        execute_query("INSERT INTO users (user_email, password) VALUES (%s, %s) ON CONFLICT(user_email) DO NOTHING", (email, hashed_password))

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
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password. Please try again.', 'error')

    return render_template('login.html')

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
                    "INSERT INTO calories (user_email, calories) VALUES ( %s, %s) ON CONFLICT (user_email) DO UPDATE SET calories = %s",
                    (user_email, calories, calories)
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
