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
    return client.post('/login', data={'username': username, 'password': password}, follow_redirects=True)

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
    response = client



def test_setup_weight_valid(client):
    """Test setting weight with valid data."""
    login(client, 'testuser', 'testpass')  # Ensure the user is logged in
    response = client.post('/setup_weight', json={
        'current_weight': 180,
        'target_weight': 160
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'Weight setup updated' in response.data  # Check for a success message or similar response

def test_setup_weight_invalid_data(client):
    """Test setting weight with invalid data (negative numbers)."""
    login(client, 'testuser', 'testpass')
    response = client.post('/setup_weight', json={
        'current_weight': -180,
        'target_weight': 160
    }, follow_redirects=True)
    assert response.status_code == 400  # Bad request due to invalid input
    assert b'error' in response.data  # Check for an error message

def test_setup_weight_unauthenticated(client):
    """Test setting weight without being logged in."""
    response = client.post('/setup_weight', json={
        'current_weight': 180,
        'target_weight': 160
    }, follow_redirects=True)
    assert response.status_code == 401  # Unauthorized or redirect to login


def test_get_calorie_deficit_logged_in(client):
    """Test fetching the calorie deficit when logged in."""
    login(client, 'testuser', 'testpass')  # Ensure the user is logged in
    response = client.get('/get-calorie-deficit')
    assert response.status_code == 200
    # Assuming the response should include a JSON with the calorie deficit
    assert 'calorie_deficit' in response.get_json()

def test_get_calorie_deficit_not_logged_in(client):
    """Test fetching the calorie deficit when not logged in."""
    response = client.get('/get-calorie-deficit')
    assert response.status_code == 401  # Expecting an unauthorized status
