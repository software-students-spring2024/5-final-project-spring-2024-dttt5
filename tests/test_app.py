# tests/test_app.py
import sys
import os
from datetime import datetime
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import pytest
from flask import url_for, session
from bson.objectid import ObjectId
from app.app import app as flask_app  

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

# For setting up weight

def test_setup_weight_not_logged_in(client):
    """Ensure unauthenticated access is prohibited."""
    response = client.post('/setup_weight', data={
        'current_weight': 70, 'target_weight': 65
    })
    assert response.status_code == 401

def test_setup_weight_missing_data(client):
    """Test missing required fields."""
    login(client, 'testuser', 'testpass')
    response = client.post('/setup_weight', data={})
    assert response.status_code == 400

def test_setup_weight_incorrect_content_type(client):
    """Test incorrect content type."""
    login(client, 'testuser', 'testpass')
    response = client.post('/setup_weight', data={
        'current_weight': 70, 'target_weight': 65
    })
    assert response.status_code == 200

def test_setup_weight_invalid_data(client):
    """Test invalid weight values."""
    login(client, 'testuser', 'testpass')
    response = client.post('/setup_weight', data={
        'current_weight': -1, 'target_weight': 0
    })
    assert response.status_code == 400

def test_setup_weight(client):
    """Test successful weight setup."""
    login(client, 'testuser', 'testpass')
    response = client.post('/setup_weight', data={
        'username':'testuser',
        'current_weight': 70, 'target_weight': 65, 
    })
    assert response.status_code == 200

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