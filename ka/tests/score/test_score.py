from ka.models import *
import random
from ka import bcrypt
from datetime import datetime, timedelta
import string
import pytest
from ka.tests.helpers import *
from ka.tests.makers import *
from sqlalchemy.exc import IntegrityError


def test_create_score_without_measures():
    user = Session.query(User).filter_by(path='test_user').first()
    s = make_score(user)
    Session.add(s)
    Session.commit()

def test_create_score_with_measures():
    user = Session.query(User).filter_by(path='test_user').first()
    s = make_score(user)
    s.measures = make_measures(random.choice(range(15)), s)
    Session.add(s)
    Session.commit()