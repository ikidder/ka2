from unittest import TestCase
from bs4 import BeautifulSoup as BS
from ka.tests.config_test import TestConfig
from ka.tests.common import ClientCase
from ka import db, create_app


def login(client, email, password):
    return client.post(
                    '/login',
                    data=dict(
                        email=email,
                        password=password
                    ),
                    content_type='application/json',
                    follow_redirects=True
    )


def logout(client):
    return client.get('/logout', follow_redirects=True)


def soup(response):
    result = BS(str(response.data), features="html.parser")
    return result


class TestMainRoutes(ClientCase):

    def test_index(self):
        with self.app.test_client() as client:
            rv = client.get('/', follow_redirects=True)
            self.assertEqual(rv.status_code, 200)
            self.assertIn(b'login', rv.data)

    def test_not_implemented_redirect_to_login(self):
        with self.app.test_client() as client:
            rv = client.get('/not_implemented', follow_redirects=True)
            self.assertEqual(rv.status_code, 200, "not_implented without login redirects to login")
            self.assertIn(b"Log In", rv.data)

    def test_not_implemented(self):
        with self.app.test_client() as client:
            login_response = login(client, 'noreply@kamagape.com', 'Password2@')
            self.assertNotIn(b'Log In', login_response.data)
            ni_response = client.get('/not_implemented')
            self.assertIn(b"We're Sorry", ni_response.data)

    # def test_not_implemented(self):
    #     with self.app.test_client() as client:
    #         login_response = login(client, 'noreply@kamagape.com', 'Password2@')
    #         self.assertEqual(login_response.status_code, 200, "log in successfully")
    #
    #         rv = client.get('/not_implemented', follow_redirects=True)
    #         #print(soup.prettify())
    #         self.assertEqual(rv.status_code, 200)
    #         self.assertIn(b'Sorry', rv.data)
