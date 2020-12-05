from bs4 import BeautifulSoup as BS
from ka.tests.config_test import TestConfig
from ka.tests.common import *
from ka import bcrypt


class TestIndex(ClientCase):

    def test_not_logged_in_gets_index(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'desire, wish, longing', response.data)


# def login(client, email, password):
#     response = client.post(
#         '/login?next=/scores',
#         data=dict(email=email, password=password),
#         #content_type='application/json',
#         #follow_redirects=True
#     )
#     print(response.headers)
#     cookie = response.headers['Set-Cookie']
#     client.set_cookie('localhost', 'session', cookie)
#
#
# def logout(client):
#     return client.get('/logout', follow_redirects=True)
#
#
# def soup(response):
#     result = BS(str(response.data), features="html.parser")
#     return result


# class TestIndexLoggedIn(LoggedInUserCase):
#
#     def test_logged_in_gets_index(self):
#         response = self.client.get('/scores', follow_redirects=True)
#         self.assertEqual(response.status_code, 200, f'actual result: {response.status_code}')
#         self.assertNotIn(b'Login', response.data)