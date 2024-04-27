from flask import Flask, request, jsonify, render_template, session, redirect, url_for
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
from bson import ObjectId
import os

app = Flask(__name__)
load_dotenv()

# Secret key for session management
app.secret_key = os.getenv("SECRET_KEY", "supersecretkey")

# Load MongoDB credentials from environment variables
username = os.getenv("MONGO_USERNAME")
password = os.getenv("MONGO_PASSWORD")
uri = os.getenv("MONGO_URI").replace('<username>', username).replace('<password>', str(password))

# Connect to MongoDB
client = MongoClient(uri)
db = client['caloriedb']
calorie_collection = db['calories']
users_collection = db['users']

@app.route('/')
def index():
    if 'username' in session:
        calorie_entries = calorie_collection.find({'username': session['username']})

        return render_template('index.html', username=session['username'], calorie_entries=calorie_entries)
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
            calorie_collection.insert_one(data)
            return jsonify(data), 201
        except Exception as e:
            print(e)  # Print the error to your Flask server log for debugging
            return jsonify({'error': 'Failed to add calories'}), 500

    else:
        user_calories = list(db.calories.find({"username": session['username']}, {'_id': 0}))
        return jsonify(user_calories)


@app.route('/calories/delete/<entry_id>', methods=['POST'])
def delete_calories(entry_id):
    if 'username' not in session:
        return jsonify({'error': 'User not logged in'}), 401
    db.calories.delete_one({'_id': entry_id, 'username': session['username']})
    return jsonify({'success': 'Entry deleted'}), 200

@app.route('/calories/edit/<entry_id>', methods=['POST'])
def edit_calories(entry_id):
    if 'username' not in session:
        return jsonify({'error': 'User not logged in'}), 401
    updated_data = request.json
    db.calories.update_one(
        {'_id': entry_id, 'username': session['username']},
        {'$set': updated_data}
    )
    return jsonify({'success': 'Entry updated'}), 200
    
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
