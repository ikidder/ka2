import os
from ka.tests.common import ContextCase
import time
from sqlalchemy.exc import IntegrityError
from ka.tests.makers import *
from ka.models import *
from sqlalchemy.exc import IntegrityError
from ka.tests.makers import *
import re


class TestTagExtract(ContextCase):

    def setUp(self):
        super().setUp()

        # create user
        name = rname()
        user = make_user(name)
        db.session.add(user)
        db.session.commit()
        self.user = user

        # create score
        score = make_score(user)
        db.session.add(score)
        db.session.commit()
        self.score = score

    def test_tag_create(self):
        tag_names = ['&each', '&for']
        self.score.text = ' '.join(tag_names)
        tags = Tag.extract_tags(self.score.text)
        self.score.tags = tags
        db.session.commit()

        self.assertEqual(2, len(self.score.tags))

    def test_tag_update(self):
        tag_names = ['&each', '&for']
        self.score.text = ' '.join(tag_names)
        tags = Tag.extract_tags(self.score.text)
        self.score.tags = tags
        db.session.commit()

        self.assertEqual(2, len(self.score.tags))

        tag_names = ['&one', '&two', '&three']
        self.score.text = ' '.join(tag_names)
        tags = Tag.extract_tags(self.score.text)
        self.score.tags = tags
        db.session.commit()

        self.assertEqual(3, len(self.score.tags))

        self.assertIn('&one', [tag.name for tag in self.score.tags])
        self.assertNotIn('&each', [tag.name for tag in self.score.tags])



