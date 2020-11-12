from unittest import TestCase
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError
from ka.tests.makers import *
import string
import time

chars = string.ascii_lowercase + string.ascii_uppercase + string.digits

def user_name():
    return ''.join(random.choice(chars) for i in range(25))


class TestNewUser(TestCase):

    Session = None

    def setUp(self):
        engine = create_engine(os.environ['DATABASE_URL'])
        self.Session = sessionmaker(bind=engine)

    def test_create_new_user(self):
        session = Session()
        name = user_name()
        u = make_user(name)
        session.add(u)
        session.commit()

        self.assertGreater(u.id, 0)
        self.assertEqual(u.path, encode(u.name))
        self.assertEqual(u.visibility, Visibility.PUBLIC)

    def test_no_duplicate_user_names(self):
        session = Session()
        name = user_name()
        u1 = make_user(name)
        session.add(u1)
        session.commit()

        with self.assertRaises(IntegrityError):
            u2 = make_user(name)
            u2.email = 'foo@example.com'
            session.add(u2)
            session.commit()

    def test_get_user_by_path(self):
        session = Session()
        user = session.query(User).filter_by(path='Paul').first()
        self.assertGreater(user.id, -1)
        self.assertEqual(user.name, 'Paul')
        self.assertEqual(user.path, 'Paul')
        #self.assertIn('@', user.email)
        self.assertIsInstance(user.text, str)
        self.assertEqual(user.visibility, Visibility.PUBLIC)

    def test_update_user(self):
        session = Session()
        user = Session.query(User).filter_by(path='Paul').first()
        user.text = ''
        user.email = user.name + '_' + str(int(time.time())) + '@example.com'
        session.add(user)
        session.commit()

