# tests/test_app.py
import sys
import os
from datetime import datetime
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import pytest
from flask import url_for, session
from bson.objectid import ObjectId
from app.app import app as flask_app  
from unittest.mock import patch
from werkzeug.security import generate_password_hash


@pytest.fixture
def mock_user_collection(mocker):
    """Fixture to mock db.users collection."""
    with patch('app.app.db.users') as mock:
        yield mock
        
@pytest.fixture(scope='module')
def app():
    """Create and configure a new app instance for each test."""
    flask_app.config.update({
        'TESTING': True,
        'SECRET_KEY': 'test',
        'SERVER_NAME': 'localhost.localdomain'  
    })
    ctx = flask_app.app_context()
    ctx.push()
    yield flask_app
    ctx.pop()

@pytest.fixture
def client(app):
    with app.test_client() as client:
        yield client

def login(client, username, password):
    with client.session_transaction() as sess:
        sess['username'] = username 

def logout(client):
    return client.get('/logout', follow_redirects=True)

def test_index_not_logged_in(client):
    """Test the index route redirects to login when user not logged in."""
    response = client.get('/')
    assert response.status_code == 302
    assert url_for('login') in response.headers['Location']


def test_logout(client):
    """Test logout functionality."""
    login(client, 'testuser', 'testpass')  
    response = logout(client)
    assert response.status_code == 200  


def test_delete_calorie_entry(client):
    """Test the deletion of a calorie entry."""
    login(client, 'testuser', 'testpass')
    entry_id = ObjectId()  # Mock an entry ID
    response = client.post(f'/calories/delete/{entry_id}', follow_redirects=True)
    assert response.status_code == 200
    # Assuming redirection to index which is successful after deletion

def test_edit_calorie_entry(client):
    """Test the editing of a calorie entry."""
    login(client, 'testuser', 'testpass')
    entry_id = ObjectId()  # Mock an entry ID
    response = client.post(f'/calories/edit/{entry_id}', data={
        'food': 'banana',
        'calories': 105,
        'date': '2021-07-20'
    }, follow_redirects=True)
    assert response.status_code == 200

def test_edit_calorie_entry_get_not_found(client, mocker):
    """Test GET request for non-existing calorie entry."""
    login(client, 'testuser', 'testpass')
    entry_id = ObjectId()
    mocker.patch('app.app.db.calories.find_one', return_value=None)

    response = client.get(f'/calories/edit/{entry_id}')
    assert response.status_code == 404

def test_edit_calorie_entry_post_failure(client, mocker):
    """Test failed update due to exception during database operation."""
    login(client, 'testuser', 'testpass')
    entry_id = ObjectId()
    mocker.patch('app.app.db.calories.update_one', side_effect=Exception("DB Error"))

    response = client.post(f'/calories/edit/{entry_id}', data={
        'food': 'apple',
        'calories': '.',
        'date': '2021-07-21'
    })
    assert response.status_code == 500
    assert 'Failed to edit calorie entry' in response.get_json()['error']


def test_add_workout(client):
    """Test adding a workout."""
    login(client, 'testuser', 'testpass')
    response = client.post('/workouts', data={
        'description': 'jogging',
        'calories_burned': 300,
        'date': '2021-07-19'
    }, follow_redirects=True)
    assert response.status_code == 200

def test_delete_workout_entry(client):
    """Test deleting a workout entry."""
    login(client, 'testuser', 'testpass')
    entry_id = ObjectId()  # Mock an entry ID
    response = client.post(f'/workouts/delete/{entry_id}', follow_redirects=True)
    assert response.status_code == 200


def test_edit_workout_entry(client):
    """Test editing a workout entry."""
    login(client, 'testuser', 'testpass')
    entry_id = ObjectId()  # Mock an entry ID
    response = client.post(f'/workouts/edit/{entry_id}', data={
        'description': 'cycling',
        'calories_burned': 250,
        'date': '2021-07-21'
    }, follow_redirects=True)
    assert response.status_code == 200

def test_edit_workout_entry_get_failure(client, mocker):
    """Test retrieving an existing workout entry for editing."""
    login(client, 'testuser', 'testpass')
    entry_id = ObjectId()
    mock_entry = {
        '_id': entry_id,
        'description': 'running',
        'calories_burned': 300,
        'date': '2021-07-21'
    }
    mocker.patch('app.app.db.workouts.find_one', return_value=mock_entry)

    response = client.get(f'/workouts/edit/{entry_id}')
    assert response.status_code == 404

def test_edit_workout_entry_get_not_found(client, mocker):
    """Test GET request for non-existing workout entry."""
    login(client, 'testuser', 'testpass')
    entry_id = ObjectId()
    mocker.patch('app.app.db.workouts.find_one', return_value=None)

    response = client.get(f'/workouts/edit/{entry_id}')
    assert response.status_code == 404

def test_edit_workout_entry_post_failure(client, mocker):
    """Test failed update due to exception during database operation."""
    login(client, 'testuser', 'testpass')
    entry_id = ObjectId()
    mocker.patch('app.app.db.workouts.update_one', side_effect=Exception("DB Error"))

    response = client.post(f'/workouts/edit/{entry_id}', data={
        'description': 'swimming',
        'calories_burned': '.',
        'date': '2021-07-22'
    })
    assert response.status_code == 500
    assert 'Failed to edit workout entry' in response.get_json()['error']



def test_setup_weight_not_logged_in(client):
    """Ensure unauthenticated access is prohibited."""
    response = client.post('/setup_weight', data={
        'current_weight': 70, 'target_weight': 65
    })
    assert response.status_code == 401


# For retrieving calorie deficit

def test_get_calorie_deficit_not_logged_in(client):
    """Ensure unauthenticated access is handled."""
    response = client.get('/get-calorie-deficit')
    assert response.status_code == 200

def test_get_calorie_deficit_no_data_available(client):
    """Test when no deficit data is available."""
    login(client, 'testuser', 'testpass')
    response = client.get('/get-calorie-deficit')
    assert response.status_code == 200

def test_get_calorie_deficit_with_data(client):
    """Test successful retrieval of calorie deficit data."""
    login(client, 'testuser', 'testpass')
    # Setup data might be needed here if your mock does not persist state
    client.post('/setup_weight', data={
        'current_weight': 80, 'target_weight': 75
    })
    response = client.get('/get-calorie-deficit')
    assert response.status_code == 200


def test_post_calories(client):
    """Test POST request for adding calorie entries."""
    login(client, 'testuser', 'testpassword')
    new_calorie_data = {
        'food': 'apple',
        'calories': 95,
        'date': '2021-08-01'
    }
    response = client.post('/calories', data=new_calorie_data)
    assert response.status_code == 302  # Expecting a redirect to 'index' after successful post

def test_post_calories_fail(client):
    """Test error handling when adding calorie entries fails."""
    login(client, 'testuser', 'testpassword')
    # Force an exception by sending incorrect data type for calories
    response = client.post('/calories', data={'food': 'apple', 'calories': 'not_a_number', 'date': '2021-08-01'})
    assert response.status_code == 500

def test_register_get(client):
    """Test retrieval of the registration form."""
    response = client.get('/register')
    assert response.status_code == 200
    assert 'Register' in response.get_data(as_text=True)

def test_register_post_success(client, mock_user_collection):
    """Test successful registration."""
    mock_user_collection.find_one.return_value = None  # No user found, allowing registration
    response = client.post('/register', data={'username': 'newuser', 'password': 'newpass'}, follow_redirects=True)
    assert response.status_code == 200
    mock_user_collection.insert_one.assert_called_once()

def test_register_post_existing_user(client, mock_user_collection):
    """Test registration with an existing username."""
    mock_user_collection.find_one.return_value = True  # User exists
    response = client.post('/register', data={'username': 'existinguser', 'password': 'password'})
    assert response.status_code == 400
    assert 'Username already exists' in response.get_data(as_text=True)

def test_login_get(client):
    """Test retrieval of the login form."""
    response = client.get('/login')
    assert response.status_code == 200
    assert 'Login' in response.get_data(as_text=True)

def test_login_post_success(client, mock_user_collection):
    """Test successful login."""
    hashed_password = generate_password_hash('testpass')
    mock_user_collection.find_one.return_value = {'username': 'testuser', 'password': hashed_password}
    response = client.post('/login', data={'username': 'testuser', 'password': 'testpass'}, follow_redirects=True)
    assert response.status_code == 200

def test_login_post_invalid(client, mock_user_collection):
    """Test login with invalid credentials."""
    mock_user_collection.find_one.return_value = {'username': 'testuser', 'password': 'testpass'}
    response = client.post('/login', data={'username': 'testuser', 'password': 'wrongpass'})
    assert response.status_code == 401
    assert 'Invalid username or password' in response.get_data(as_text=True)