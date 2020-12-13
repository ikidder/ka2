import os
from ka.tests.common import ContextCase
import time
from sqlalchemy.exc import IntegrityError
from ka.tests.makers import *
from ka.models import *
from sqlalchemy.exc import IntegrityError
from ka.tests.makers import *


class TestDeleteTags(ContextCase):

    def setUp(self):
        super().setUp()

        # create users
        user_names = [rname() for i in range(5)]
        self.users = []
        for name in user_names:
            user = make_user(name)
            db.session.add(user)
            db.session.commit()
            self.users.append(user)

        # create scores
        for i in range(5):
            score = make_score(random.choice(self.users))
            count_measures = rint(1, 20)
            score.measures = make_measures(count_measures, score)
            db.session.add(score)
            db.session.commit()

        # create posts
        for i in range(5):
            post = make_post(random.choice(self.users))
            db.session.add(post)
            db.session.commit()

    def test_delete_tags(self):
        post = Post.query.first()
        score = Score.query.first()

        # create tags
        t1 = Tag('&EdfdN')
        t2 = Tag('&Ûdfa8F')
        db.session.add(t1)
        db.session.add(t2)

        # tag objects
        t1.tagged.append(post)
        t1.tagged.append(score)
        t2.tagged.append(score)
        db.session.commit()

        # remove one of the t1 tags
        t1.tagged = t1.tagged[:1]
        db.session.commit()
        self.assertEqual(1, len(t1.tagged), 'length of t1 after removal')

        # remove the only t2 tag
        t2.tagged = []
        db.session.commit()
        self.assertEqual(0, len(t2.tagged), 'length of t2 after removal')

        # make sure the content wasn't cascade deleted
        scores = Score.query.all()
        self.assertIn(score, scores, 'the score still exists')
        posts = Post.query.all()
        self.assertIn(post, posts)