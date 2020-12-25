import pytest
from ka import bcrypt
from bs4 import BeautifulSoup as BS
from ka.tests.config_test import TestConfig
from ka import db, create_app
from ka.tests.common import TEST_USER_NAME, TEST_USER_EMAIL, TEST_USER_PW, make_user



@pytest.fixture
def state():
    app = create_app(TestConfig)
    ctx = app.test_request_context()
    ctx.push()
    with app.test_client() as client:
        db.create_all()

        yield app, db, client

    db.session.remove()
    db.drop_all()
    ctx.pop()


def login(client, email, password):
    response = client.post('/login', data=dict(
        email=email,
        password=password
    ), follow_redirects=True)
    return response


def logout(client):
    return client.get('/logout', follow_redirects=True)


def soup(response):
    result = BS(str(response.data), features="html.parser")
    return result


def test_get_index(state):
    app, ctx, client = state
    response = client.get('/')
    assert response.status_code == 200
    assert b'desire, wish, longing' in response.data


def test_login(state):
    app, db, client = state

    user = make_user(TEST_USER_NAME)
    user.email = TEST_USER_EMAIL
    user.password = bcrypt.generate_password_hash(TEST_USER_PW).decode('utf-8')
    db.session.add(user)
    db.session.commit()

    rv = login(client, TEST_USER_EMAIL, TEST_USER_PW)
    assert b'Login' not in rv.data


def test_get_after_login(state):
    app, db, client = state

    user = make_user(TEST_USER_NAME)
    user.email = TEST_USER_EMAIL
    user.password = bcrypt.generate_password_hash(TEST_USER_PW).decode('utf-8')
    db.session.add(user)
    db.session.commit()

    login(client, TEST_USER_EMAIL, TEST_USER_PW)
    response = client.get('/composers')
    assert response.status_code == 200
