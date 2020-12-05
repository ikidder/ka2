import os
from ka.tests.common import ContextCase
import time
from sqlalchemy.exc import IntegrityError
from ka.tests.makers import *
from ka.models import *
from sqlalchemy.exc import IntegrityError
from ka.tests.makers import *


class TestCreateScore(ContextCase):

    def setUp(self):
        super().setUp()
        self.name = rname()
        user = make_user(self.name)
        db.session.add(user)
        db.session.commit()

    def test_create_score_without_measures(self):
        user = User.query.filter(User.name == self.name).first()

        score = make_score(user)
        db.session.add(score)
        db.session.commit()

        self.assertGreater(score.id, 0)
        self.assertEqual(len(score.measures), 0)

    def test_create_score_with_measures(self):
        user = User.query.filter(User.name == self.name).first()

        score = make_score(user)
        count_measures = rint(1, 20)
        score.measures = make_measures(count_measures, score)
        db.session.add(score)
        db.session.commit()

        self.assertGreater(score.id, 0)
        self.assertEqual(len(score.measures), count_measures)