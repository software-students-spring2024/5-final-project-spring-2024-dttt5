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
        user_collection = db.users
        try:
            data = {
                "username": session['username'],
                "food": request.form['food'],
                "calories": int(request.form['calories']),
                "date": request.form['date']
            }
            db.calories.insert_one(data)

            # get current user information for calorie management
            user_info = user_collection.find_one({"username": session['username']})
            if user_info and 'total_calorie_deficit_needed' in user_info:
                base_intake = 2500
                daily_deficit = base_intake - data['calories']
                new_total_deficit = user_info['total_calorie_deficit_needed'] - daily_deficit
                # Update the total calorie deficit needed
                user_collection.update_one({"username": session['username']}, {"$set": {"total_calorie_deficit_needed": new_total_deficit}})

            return redirect(url_for('index'))
        except Exception as e:
            print(e)
            return jsonify({'error': 'Failed to add calories'}), 500

    else:
        user_calories = list(db.calories.find({"username": session['username']}, {'_id': 1, 'food': 1, 'calories': 1, 'date': 1}))
        return jsonify(user_calories)
    
@app.route('/setup_weight', methods=['GET', 'POST'])
def setup_weight():
    if 'username' not in session:
        return jsonify({'error': 'User not logged in'}), 401
    
    try:
        current_weight = float(request.json['current_weight'])
        target_weight = float(request.json['target_weight'])
        total_calorie_deficit_needed = (current_weight - target_weight) * 3500
        
        db.users.update_one(
            {"username": session['username']},
            {"$set": {
                "current_weight": current_weight,
                "target_weight": target_weight,
                "total_calorie_deficit_needed": total_calorie_deficit_needed
            }}
        )
        return jsonify({'message': 'Weight setup updated'}), 200
    except Exception as e:
        print(e)
        return jsonify({'error': 'Failed to setup weight'}), 500

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
