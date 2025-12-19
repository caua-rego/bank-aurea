import pytest
from app import create_app, db
from app.models.user import User
from app.models.account import Account

@pytest.fixture
def app():
    app = create_app('testing')
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def auth_client(client, app):
    # Register and Login
    with app.app_context():
        client.post('/register', data={
            'username': 'testuser', 
            'email': 'test@test.com', 
            'password': 'password',
            'confirm_password': 'password'
        }, follow_redirects=True)
    return client

def test_registration(client, app):
    response = client.post('/register', data={
        'username': 'newuser', 
        'email': 'new@test.com', 
        'password': 'password',
        'confirm_password': 'password'
    }, follow_redirects=True)
    assert response.status_code == 200
    # Check if account was created
    with app.app_context():
        user = User.query.filter_by(username='newuser').first()
        assert user is not None
        account = Account.query.filter_by(user_id=user.id).first()
        assert account is not None
        assert account.balance == 1000.0

def test_login(auth_client):
    response = auth_client.post('/login', data={
        'email': 'test@test.com',
        'password': 'password'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'Welcome, testuser' in response.data

def test_transfer_security(auth_client, app):
    # Login first
    auth_client.post('/login', data={'email': 'test@test.com', 'password': 'password'}, follow_redirects=True)
    
    # Create target user
    with app.app_context():
        u2 = User(username='target', email='target@test.com')
        u2.set_password('password')
        db.session.add(u2)
        db.session.commit()
        # Create acc 2
        acc2 = Account(number='99999', user_id=u2.id, balance=0.0)
        db.session.add(acc2)
        db.session.commit()
    
    # Try transfer
    response = auth_client.post('/transfer', data={
        'target_account': '99999',
        'amount': '100.0'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b'Transfer successful' in response.data
    
    with app.app_context():
        acc2 = Account.query.filter_by(number='99999').first()
        assert acc2.balance == 100.0
