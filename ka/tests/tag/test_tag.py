import os
from ka.tests.common import ContextCase
import time
from sqlalchemy.exc import IntegrityError
from ka.tests.makers import *
from ka.models import *
from sqlalchemy.exc import IntegrityError
from ka.tests.makers import *


class TestCreateTag(ContextCase):

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

    def test_create_tag(self):
        name = '&first'
        t = Tag(name)
        db.session.add(t)
        db.session.commit()
        self.assertGreater(t.id, 0)
        self.assertEqual(t.name, name)

    def test_create_tag_with_non_english_char(self):
        name = '&firstē'
        t = Tag(name)
        db.session.add(t)
        db.session.commit()
        self.assertGreater(t.id, 0)
        self.assertEqual(t.name, name)

    def test_create_tag_with_caps(self):
        name = '&FiRstē'
        t = Tag(name)
        db.session.add(t)
        db.session.commit()
        self.assertGreater(t.id, 0)
        self.assertEqual(t.name, name)

    def test_tag_score(self):
        t = Tag('&first')
        db.session.add(t)
        db.session.commit()

        score = Score.query.first()
        t.tagged.append(score)
        db.session.commit()

        self.assertEqual(t.tagged[0].id, score.id)

    def test_tag_post(self):
        t = Tag('&first')
        db.session.add(t)
        db.session.commit()

        post = Post.query.first()
        t.tagged.append(post)
        db.session.commit()

        self.assertEqual(t.tagged[0].id, post.id)

    def test_tag_multiple(self):
        t = Tag('&EdfdN')
        db.session.add(t)
        db.session.commit()

        posts = Post.query.all()
        scores = Score.query.all()

        for post in posts:
            t.tagged.append(post)
        for score in scores:
            t.tagged.append(score)

        db.session.commit()

        self.assertEqual(len(t.tagged), len(posts) + len(scores))
        self.assertIn(posts[1], t.tagged)
        self.assertIn(scores[0], t.tagged)



