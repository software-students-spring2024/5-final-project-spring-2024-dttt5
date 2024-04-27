from flask import Flask, request, jsonify, render_template, session, redirect, url_for
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
from bson.objectid import ObjectId
import os

app = Flask(__name__)
load_dotenv()

app.secret_key = os.getenv("SECRET_KEY", "supersecretkey")

username = os.getenv("MONGO_USERNAME")
password = os.getenv("MONGO_PASSWORD")
uri = os.getenv("MONGO_URI").replace('<username>', username).replace('<password>', password)

client = MongoClient(uri)
db = client['caloriedb']

@app.route('/')
def index():
    if 'username' in session:
        user_calories = list(db.calories.find({"username": session['username']}, {'_id': 1, 'food': 1, 'calories': 1, 'date': 1}))
        total_calories = sum(entry['calories'] for entry in user_calories)
        return render_template('index.html', username=session['username'], user_calories=user_calories, total_calories=total_calories)
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
                "food": request.form['food'],
                "calories": int(request.form['calories']),
                "date": request.form['date']
            }
            db.calories.insert_one(data)
            return redirect(url_for('index'))
        except Exception as e:
            print(e)
            return jsonify({'error': 'Failed to add calories'}), 500

    else:
        user_calories = list(db.calories.find({"username": session['username']}, {'_id': 1, 'food': 1, 'calories': 1, 'date': 1}))
        return jsonify(user_calories)
    
@app.route('/setup_weight', methods=['GET', 'POST'])
def setup_weight():
    #
    return

@app.route('/calories/delete/<entry_id>', methods=['POST'])
def delete_calorie_entry(entry_id):
    if 'username' not in session:
        return redirect(url_for('login'))

    db.calories.delete_one({"_id": ObjectId(entry_id), "username": session['username']})
    return redirect(url_for('index'))

@app.route('/calories/edit/<entry_id>', methods=['GET', 'POST'])
def edit_calorie_entry(entry_id):
    if 'username' not in session:
        return redirect(url_for('login'))

    if request.method == 'GET':
        entry = db.calories.find_one({"_id": ObjectId(entry_id), "username": session['username']})
        if entry:
            return render_template('edit_calorie_entry.html', entry=entry)
        else:
            return 'Entry not found', 404
    elif request.method == 'POST':
        try:
            update_data = {
                "food": request.form['food'],
                "calories": int(request.form['calories']),
                "date": request.form['date']
            }
            db.calories.update_one({"_id": ObjectId(entry_id), "username": session['username']}, {"$set": update_data})
            return redirect(url_for('index'))
        except Exception as e:
            print(e)
            return jsonify({'error': 'Failed to edit calorie entry'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
