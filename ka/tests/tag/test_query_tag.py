import os
from ka.tests.common import ContextCase
import time
from sqlalchemy.exc import IntegrityError
from ka.tests.makers import *
from ka.models import *
from sqlalchemy.exc import IntegrityError
from ka.tests.makers import *


class TestQueryTagged(ContextCase):

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

    def test_get_tags(self):
        posts = Post.query.all()
        scores = Score.query.all()

        # create tags
        t1 = Tag('&EdfdN')
        t2 = Tag('&Ûdfa8F')
        t3 = Tag('&upanddownandaround')
        db.session.add(t1)
        db.session.add(t2)
        db.session.add(t3)

        # tag objects
        t1.tagged.append(posts[0])
        t1.tagged.append(scores[0])
        t2.tagged.append(scores[1])
        db.session.commit()

        tag_counts = Tag.tag_counts()
        self.assertEqual(len(tag_counts), 2, 'three tags created, but only two have tagged objects')

        for name, count in tag_counts:
            if name == t1.name:
                self.assertEqual(count, 2, 't1 count')
            elif name == t2.name:
                self.assertEqual(count, 1, 't2 count')
            else:
                raise Exception(f'tag with name {name} was not recognized')

    def test_get_tags_from_objects(self):
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

        post_tags = post.tags
        score_tags = score.tags

        self.assertEqual(len(post_tags), 1, 'the post has one tag')
        self.assertEqual(len(score_tags), 2, 'the score has two tags')

