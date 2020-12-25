from unittest import TestCase
import os
import random
import string
from ka.tests.config_test import TestConfig
from ka import db, create_app
from ka.models import User
from ka.tests.makers import make_user
from bs4 import BeautifulSoup as BS
from ka import bcrypt


class ContextCase(TestCase):

    def setUp(self):
        self.app = create_app(TestConfig)
        self.ctx = self.app.test_request_context()
        self.ctx.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.ctx.pop()


class ClientCase(ContextCase):

    def setUp(self):
        super().setUp()
        self.client = self.app.test_client()


TEST_USER_NAME = 'Paul'
TEST_USER_EMAIL = TEST_USER_NAME + '@example.com'
TEST_USER_PW = '1234'  # haha




# class LoggedInUserCase(ClientCase):
#
#     def setUp(self):
#         super().setUp()
#
#         user = User(name=TEST_USER_NAME)
#         user.email = TEST_USER_EMAIL
#         user.password = bcrypt.generate_password_hash(TEST_USER_PW).decode('utf-8')
#         user.text = 'starting text for default test user'
#
#         db.session.add(user)
#         db.session.commit()
#
#         self.login(TEST_USER_EMAIL, TEST_USER_PW)
#
#     def login(self, email, password):
#         response = self.client.post(
#             '/login',
#             data=dict(email=email, password=password),
#             # content_type='application/json',
#             # follow_redirects=True
#         )
#         print(response.headers)
#         cookie = response.headers['Set-Cookie']
#         self.client.set_cookie('localhost', 'session', cookie)
#
#     def logout(self):
#         return self.client.get('/logout', follow_redirects=True)
#
#     def soup(response):
#         result = BS(str(response.data), features="html.parser")
#         return result
