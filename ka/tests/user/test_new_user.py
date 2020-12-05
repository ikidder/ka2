import os
import random
from ka.tests.config_test import TestConfig
from ka.tests.common import ContextCase
from ka import db, create_app
import string
import time
from sqlalchemy.exc import IntegrityError
from ka.tests.makers import make_user, make_default_users, rname, chars
from ka.models import User, encode, Visibility


class TestNewUser(ContextCase):

    def test_create_new_user(self):
        name = rname()
        u = make_user(name)
        db.session.add(u)
        db.session.commit()

        self.assertGreater(u.id, 0)
        self.assertEqual(u.path, encode(u.name))
        self.assertEqual(u.visibility, Visibility.PUBLIC)

    def test_no_duplicate_user_names(self):
        name = rname()
        u1 = make_user(name)
        db.session.add(u1)
        db.session.commit()

        with self.assertRaises(IntegrityError):
            u2 = make_user(name)
            u2.email = 'foo@example.com'
            db.session.add(u2)
            db.session.commit()

    def test_no_duplicate_emails(self):
        email = 'foo@example.com'
        u1 = make_user(rname())
        u1.email = email
        db.session.add(u1)
        db.session.commit()

        with self.assertRaises(IntegrityError):
            u2 = make_user(rname())
            u2.email = email
            db.session.add(u2)
            db.session.commit()

    def test_get_user_by_path(self):
        name = 'Paul'
        u = make_user(name)
        db.session.add(u)
        db.session.commit()
        user = User.query.filter_by(path=name).first()
        self.assertGreater(user.id, -1)
        self.assertEqual(user.name, name)
        self.assertEqual(user.path, encode(name))
        self.assertIn('@', user.email)
        self.assertIsInstance(user.text, str)
        self.assertEqual(user.visibility, Visibility.PUBLIC)

    def test_update_user(self):
        name = 'Paul'
        u = make_user(name)
        db.session.add(u)
        db.session.commit()
        user = User.query.filter_by(path='Paul').first()
        user.text = str([random.choice(chars) for i in range(20)])
        user.email = user.name + '_' + str(int(time.time())) + '@example.com'
        db.session.add(user)
        db.session.commit()

