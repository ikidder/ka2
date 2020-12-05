import os
import random
from ka.tests.config_test import TestConfig
from ka.tests.common import ContextCase
from ka import db, create_app
import string
import time
from sqlalchemy.exc import IntegrityError
from ka.tests.makers import *
from ka.models import User, encode, Visibility


class TestGetUser(ContextCase):

    def setUp(self):
        super().setUp()
        self.name = rname()
        user = make_user(self.name)
        db.session.add(user)
        db.session.commit()
        self.user_id = user.id
        self.user_email = user.email

    def test_user_get_by_id(self):
        user = User.query.get(self.user_id)
        self.assertEqual(user.name, self.name)

    def test_user_get_by_path(self):
        user = User.query.filter(User.path == encode(self.name)).first()
        self.assertEqual(user.name, self.name)

    def test_user_get_by_email(self):
        user = User.query.filter(User.email == self.user_email).first()
        self.assertEqual(user.name, self.name)