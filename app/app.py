from flask import Flask, request, jsonify, render_template, session, redirect, url_for
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
from bson.objectid import ObjectId
import os

app = Flask(__name__)
load_dotenv()
#should work now with git
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
        user_workouts = list(db.workouts.find({"username": session['username']}, {'_id': 1, 'description': 1, 'calories_burned': 1, 'date': 1}))
        total_calories = sum(entry['calories'] for entry in user_calories)
        total_burned = sum(entry['calories_burned'] for entry in user_workouts)

        user_info = db.users.find_one({"username": session['username']})

        if user_info and 'total_calorie_deficit_needed' in user_info:
            total_calorie_deficit_needed = user_info['total_calorie_deficit_needed']
        else:
            # not yet setup weight
            total_calorie_deficit_needed = 0

        return render_template('index.html', username=session['username'], user_calories=user_calories, total_calories=total_calories-total_burned, total_burned=total_burned, user_workouts=user_workouts, total_calorie_deficit_needed=total_calorie_deficit_needed)
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

@app.route('/logout', methods=['GET', 'POST'])
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
        if current_weight <= 0 or target_weight <= 0:
            raise ValueError("Weights must be positive numbers.")

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
    except KeyError as ke:
        return jsonify({'error': f'Missing key: {str(ke)}'}), 400
    except ValueError as ve:
        print(ve)
        return jsonify({'error': str(ve)}), 400
    except Exception as e:
        print(e)
        return jsonify({'error': 'Failed to setup weight'}), 500
    
@app.route('/get-calorie-deficit')
def get_calorie_deficit():
    user_info = db.users.find_one({"username": session.get('username')})
    if user_info and 'total_calorie_deficit_needed' in user_info:
        return jsonify(calorie_deficit=user_info['total_calorie_deficit_needed'])
    return jsonify(calorie_deficit=0)


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

@app.route('/workouts', methods=['GET', 'POST'])
def workouts():
    if 'username' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        try:
            data = {
                "username": session['username'],
                "description": request.form['description'],
                "calories_burned": int(request.form['calories_burned']),
                "date": request.form['date']
            }
            db.workouts.insert_one(data)
            return redirect(url_for('index'))
        except Exception as e:
            print(e)
            return jsonify({'error': 'Failed to add workout'}), 500

    else:
        user_workouts = list(db.workouts.find({"username": session['username']}, {'_id': 1, 'description': 1, 'calories_burned': 1, 'date': 1}))
        return jsonify(user_workouts)

@app.route('/workouts/delete/<entry_id>', methods=['POST'])
def delete_workout_entry(entry_id):
    if 'username' not in session:
        return redirect(url_for('login'))

    db.workouts.delete_one({"_id": ObjectId(entry_id), "username": session['username']})
    return redirect(url_for('index'))

@app.route('/workouts/edit/<entry_id>', methods=['GET', 'POST'])
def edit_workout_entry(entry_id):
    if 'username' not in session:
        return redirect(url_for('login'))

    if request.method == 'GET':
        entry = db.workouts.find_one({"_id": ObjectId(entry_id), "username": session['username']})
        if entry:
            return render_template('edit_workout_entry.html', entry=entry)
        else:
            return 'Entry not found', 404
    elif request.method == 'POST':
        try:
            update_data = {
                "description": request.form['description'],
                "calories_burned": int(request.form['calories_burned']),
                "date": request.form['date']
            }
            db.workouts.update_one({"_id": ObjectId(entry_id), "username": session['username']}, {"$set": update_data})
            return redirect(url_for('index'))
        except Exception as e:
            print(e)
            return jsonify({'error': 'Failed to edit workout entry'}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)