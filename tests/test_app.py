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

def test_register(client):
    """Test the registration functionality."""
    with patch('app.app.db.users.find_one') as mock_find_one:
        mock_find_one.return_value = None  # Simulate that the username doesn't exist
        response = client.post('/register', data={
            'username': 'newuser',
            'password': 'newpassword'
        }, follow_redirects=True)
        assert response.status_code == 200
        assert b'Redirecting' in response.data  # Check if the user is redirected to the login page

def test_logout(client):
    """Test logout functionality."""
    login(client, 'testuser', 'testpass')
    with client.session_transaction() as sess:
        assert 'username' in sess
    response = logout(client)
    assert response.status_code == 302
    assert url_for('login') in response.headers['Location']
    with client.session_transaction() as sess:
        assert 'username' not in sess