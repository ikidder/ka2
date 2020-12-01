from unittest import TestCase
# from ka import create_app, engine, Session
from bs4 import BeautifulSoup as BS
import requests

def login(client, email, password):
    return client.post('/login', data=dict(
                            email=email,
                            password=password
                        ),
                       content_type='application/json',
                       follow_redirects=True)


def logout(client):
    return client.get('/logout', follow_redirects=True)


# def soup(response):
#     result = BS(str(response.data), features="html.parser")
#     return result

def soup(response):
    result = BS(str(response.content), features="html.parser")
    return result


class TestMainRoutes(TestCase):

    # @classmethod
    # def setUpClass(cls):
    #     cls.app = create_app()
    #     cls.app.config['TESTING'] = True
    #     cls.app.config['WTF_CSRF_ENABLED'] = False

    # def test_index(self):
    #     with self.app.test_client() as client:
    #         rv = client.get('/', follow_redirects=True)
    #         self.assertEqual(rv.status_code, 200)
    #         self.assertIn(b'login', rv.data)
    #
    # def test_not_implemented_redirect_to_login(self):
    #     with self.app.test_client() as client:
    #         rv = client.get('/not_implemented', follow_redirects=True)
    #         self.assertEqual(rv.status_code, 200, "not_implented without login redirects to login")
    #         self.assertIn(b"Log In", rv.data)
            
    
    def test_login_with_requests(self):
        r = requests.get('http://127.0.0.1:5000/login')
        s = soup(r)
        csrf = s.find(id='csrf_token').attrs['value']
        self.assertIsNotNone(csrf, 'csrf found')
        r = requests.post('http://127.0.0.1:5000/login', data={'email': 'noreply@kamagape.com', 'password': 'Password2@'})
        print(r)
        print(r.status_code)
        self.assertNotIn('Log In', r.text)
    

    # def test_not_implemented(self):
    #     with self.app.test_client() as client:
    #         login_response = login(client, 'noreply@kamagape.com', 'Password2@')
    #         print(login_response.status_code)
    #         print(soup(login_response).prettify())
    #         self.assertNotIn(b'Log In', login_response.data)


    # def test_not_implemented(self):
    #     with self.app.test_client() as client:
    #         login_response = login(client, 'noreply@kamagape.com', 'Password2@')
    #         self.assertEqual(login_response.status_code, 200, "log in successfully")
    #
    #         rv = client.get('/not_implemented', follow_redirects=True)
    #         #print(soup.prettify())
    #         self.assertEqual(rv.status_code, 200)
    #         self.assertIn(b'Sorry', rv.data)
