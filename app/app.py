from flask import Flask, request, jsonify, render_template, session, redirect, url_for
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
import os

app = Flask(__name__)
load_dotenv()

# Secret key for session management
app.secret_key = os.getenv("SECRET_KEY", "supersecretkey")

# Load MongoDB credentials from environment variables
username = os.getenv("MONGO_USERNAME")
password = os.getenv("MONGO_PASSWORD")
uri = os.getenv("MONGO_URI").replace('<username>', username).replace('<password>', password)

# Connect to MongoDB
client = MongoClient(uri)
db = client['caloriedb']

@app.route('/')
def index():
    if 'username' in session:
        return render_template('index.html', username=session['username'])
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user_collection = db.users

        if user_collection.find_one({"username": username}):
            return "Username already exists", 400

        hashed_password = generate_password_hash(password)
        user_collection.insert_one({"username": username, "password": hashed_password})
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user_collection = db.users

        user = user_collection.find_one({"username": username})
        if user and check_password_hash(user['password'], password):
            session['username'] = username
            return redirect(url_for('index'))
        return "Invalid username or password", 401
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/calories', methods=['GET', 'POST'])
def calories():
    if 'username' not in session:
        return jsonify({'error': 'User not logged in'}), 401

    if request.method == 'POST':
        try:
            data = {
                "username": session['username'],
                "food": request.json['food'],
                "calories": request.json['calories'],
                "date": request.json['date']
            }
            db.calories.insert_one(data)
            return jsonify(data), 201
        except Exception as e:
            print(e)  # Print the error to your Flask server log for debugging
            return jsonify({'error': 'Failed to add calories'}), 500

    else:
        user_calories = list(db.calories.find({"username": session['username']}, {'_id': 0}))
        return jsonify(user_calories)


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
