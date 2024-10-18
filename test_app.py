import pytest
from app import app, db, User, UserBooks
from flask import url_for
from unittest.mock import patch

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'  # Use in-memory DB for tests
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client
        with app.app_context():
            db.drop_all()

def test_create_user(client):
    # Test user registration
    response = client.post('/register', data={
        'username': 'test_user',
        'password': 'test_password'
    }, follow_redirects=True)
    assert response.status_code == 200
    user = User.query.filter_by(username='test_user').first()
    assert user is not None

def test_login(client):
    # Create user manually for login test
    user = User(username='test_user')
    user.set_password('test_password')
    db.session.add(user)
    db.session.commit()

    # Test login functionality
    response = client.post('/login', data={
        'username': 'test_user',
        'password': 'test_password'
    })
    assert response.status_code == 302  # Redirect on successful login

def test_add_book(client):
    # Add book to UserBooks table
    user = User(username='test_user')
    user.set_password('test_password')
    db.session.add(user)
    db.session.commit()

    response = client.post('/add_book', data={
        'title': 'Test Book',
        'author': 'Test Author',
        'year_published': 2022,
        'price': 9.99
    })
    assert response.status_code == 200
    book = UserBooks.query.filter_by(title='Test Book').first()
    assert book is not None
    assert book.author == 'Test Author'

def test_recommend_books(client):
    # Test book recommendation route
    response = client.get('/recommend?query=test')
    assert response.status_code == 200
    assert b'Suggestions' in response.data
