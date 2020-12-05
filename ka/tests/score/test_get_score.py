import os
from ka.tests.common import ContextCase
import time
from sqlalchemy.exc import IntegrityError
from ka.tests.makers import *
from ka.models import *
from sqlalchemy.exc import IntegrityError
from sqlalchemy import or_
from ka.tests.makers import *


class TestGetScore(ContextCase):

    def setUp(self):
        super().setUp()
        self.user_name = rname()
        user = make_user(self.user_name)
        db.session.add(user)
        db.session.commit()

        score = make_score(user)
        count_measures = rint(1, 20)
        score.measures = make_measures(count_measures, score)
        db.session.add(score)
        db.session.commit()

        self.score_name = score.name
        self.score_path = score.path
        self.score_id = score.id

    def test_get_score_by_path(self):
        score = Score.query.filter(Score.path == self.score_path).first()
        self.assertEqual(score.id, self.score_id)

    def test_get_score_by_user(self):
        user = User.query.filter(User.name == self.user_name).first()
        score = Score.query\
            .filter(Score.user_id == user.id)\
            .first()
        self.assertEqual(score.id, self.score_id)

