from ka.models import *
import random
from unittest import TestCase
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError
from ka.tests.makers import *
import string
import time


class TestNewScore(TestCase):

    Session = None

    def setUp(self):
        engine = create_engine(os.environ['DATABASE_URL'])
        self.Session = sessionmaker(bind=engine)

    def test_create_score_without_measures(self):
        session = Session()
        score_name = 'Test Score ' + '_' + str(int(time.time()))
        user = session.query(User).filter_by(path='test_user').first()
        s = make_score(user)
        s.name = score_name
        Session.add(s)
        Session.commit()

        self.assertEqual(s.composer.path, 'test_user')
        self.assertEqual(len(s.measures), 0)

    def test_create_score_with_measures(self):
        session = Session()
        user = session.query(User).filter_by(path='test_user').first()
        s = make_score(user)
        s.measures = make_measures(random.choice(range(15)), s)
        session.add(s)
        session.commit()