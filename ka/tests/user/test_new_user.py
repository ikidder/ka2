from unittest import TestCase
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError
from ka.tests.makers import *
import string

chars = string.ascii_lowercase + string.ascii_uppercase + string.digits

def user_name():
    return ''.join(random.choice(chars) for i in range(15))


class TestNewUser(TestCase):

    Session = None

    def setUp(self):
        engine = create_engine(os.environ['DATABASE_URL'])
        self.Session = scoped_session(sessionmaker(bind=engine))

    def tearDown(self):
        self.Session.remove()

    def test_create_new_user(self):
        name = user_name()
        u = make_user(name)
        Session.add(u)
        Session.commit()

        assert u.id > 0
        assert u.path == encode(u.name)
        assert u.visibility == Visibility.PUBLIC

    def test_no_duplicate_user_names(self):
        name = user_name()
        u1 = make_user(name)
        Session.add(u1)
        Session.commit()

        with self.assertRaises(IntegrityError):
            u2 = make_user(name)
            u2.email = 'foo@example.com'
            Session.add(u2)
            Session.commit()

