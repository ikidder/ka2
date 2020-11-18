from dataclasses import dataclass
from datetime import datetime
from time import time
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app
import jwt
from urllib.parse import quote
from enum import Enum, unique
from ka import login_manager
from ka import Session
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship, backref, validates, joinedload
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Index, event, and_
from sqlalchemy import Enum as dbEnum
from sqlalchemy.orm import with_polymorphic
from flask_login import UserMixin


# Reminder: app can be accessed with a flask variable:
#from flask import current_app


# *************************************************
#  Common
# *************************************************

Base = declarative_base()


def encode(s):
    s = s.strip().replace(' ', '-')
    return quote(s, safe='', encoding='utf-8', errors='strict')


@unique
class Visibility(Enum):
    PUBLIC = 'PUBLIC'      # appears in general lists and searches
    PRIVATE = 'PRIVATE'    # can be accessed with a direct link, or through the user's page
    HIDDEN = 'HIDDEN'      # will not appear on the site at all


def pp_duration(seconds: int) -> str:
    """Returns a formatted string showing hours, minutes, and seconds.
    >>> pp_duration(5)
    '00:05'
    >>> pp_duration(61)
    '01:01'
    >>> pp_duration(3600)
    '1:00:00'
    >>> pp_duration(36000)
    '10:00:00'
    """
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    if h > 0:
        return '{:d}:{:02d}:{:02d}'.format(h, m, s)
    else:
        return '{:02d}:{:02d}'.format(m, s)


def to_ordinal_string(n: int) -> str:
    """Converts an integer into its ordinal representation.
    >>> to_ordinal_string(0)
    '0th'
    >>> to_ordinal_string(3)
    '3rd'
    >>> to_ordinal_string(122)
    '122nd'
    >>> to_ordinal_string(213)
    '213th'
    """
    # source: https://stackoverflow.com/a/50992575
    n = int(n)
    suffix = ['th', 'st', 'nd', 'rd', 'th'][min(n % 10, 4)]
    if 11 <= (n % 100) <= 13:
        suffix = 'th'
    return str(n) + suffix


PER_PAGE = 10

@dataclass
class PageResult:
    items: list
    current_page: int
    has_prev: bool
    has_next: bool


# TODO - just, in general, TODO
def get_page(q, page):
    results = q.limit(PER_PAGE + 1).offset((page - 1) * PER_PAGE).all()
    has_prev = True if page > 1 else False
    has_next = True if len(results) == (PER_PAGE + 1) else False
    results = results[:PER_PAGE]
    return PageResult(results, page, has_prev, has_next)


@event.listens_for(Session, "before_flush")
def before_flush(session, flush_context, instances):
    for instance in session.dirty:
        if isinstance(instance, Post) or isinstance(instance, Score) or isinstance(instance, Measure):
            instance.validate()
    for instance in session.new:
        if isinstance(instance, Post) or isinstance(instance, Score) or isinstance(instance, Measure):
            instance.validate()
    for instance in session.deleted:
        if isinstance(instance, Post) or isinstance(instance, Score) or isinstance(instance, Measure):
            instance.validate()


# *************************************************
#  KaBase
# *************************************************


class KaBase(Base):
    __tablename__ = 'kabase'
    id = Column(Integer, primary_key=True)
    _name = Column(String(200), nullable=False)
    _path = Column(String(650), nullable=False)  # see Measure path formatting for the reason this is long
    type = Column(String(50))
    created = Column(DateTime, default=datetime.utcnow)

    __mapper_args__ = {
        'polymorphic_identity': 'kabase',
        'polymorphic_on': type
    }

    __table_args__ = (Index('_path_type_unique_index', _path, type, unique=True),)


# *************************************************
#  User
# *************************************************


@login_manager.user_loader
def load_player(user_id):
    return Session.query(User).get(int(user_id))


class User(KaBase, UserMixin):
    __tablename__ = 'user'

    id = Column(ForeignKey("kabase.id"), primary_key=True)
    email = Column(String(120), unique=True, nullable=False)
    confirmed = Column(DateTime, nullable=True)
    password = Column(String(60), nullable=False)
    visibility = Column('visibility', dbEnum(Visibility), default=Visibility.PUBLIC)
    text = Column(Text, nullable=True, default='')
    count_favorites = Column(Integer, nullable=False, default=0)
    count_scores = Column(Integer, nullable=False, default=0)
    count_posts = Column(Integer, nullable=False, default=0)
    count_tours = Column(Integer, nullable=False, default=0)
    invites_left = Column(Integer, nullable=False, default=5)

    @hybrid_property
    def name(self):
        return self._name

    @hybrid_property
    def path(self):
        return self._path

    __searchable__ = ['username']

    __mapper_args__ = {
        'polymorphic_identity': 'user',
    }

    def favorites(self):
        favoritable = with_polymorphic(KaBase, [User, Score, Post], flat=True)
        favs = Session.query(Favorite)\
            .options(joinedload(Favorite.content.of_type(favoritable)))\
            .filter(Favorite.user_id == self.id)\
            .order_by(Favorite.created.desc())\
            .all()
        return [fav.content for fav in favs]

    def get_favorite(self, kabase_id):
        return Session.query(Favorite) \
            .filter(and_(Favorite.user_id == self.id, Favorite.content_id == kabase_id)) \
            .first()

    def get_reset_password_token(self, expires_in=600):
        return jwt.encode(
            {'reset_password': self.id, 'exp': time() + expires_in},
            current_app.config['SECRET_KEY'], algorithm='HS256').decode('utf-8')

    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token, current_app.config['SECRET_KEY'],
                            algorithms=['HS256'])['reset_password']
        except:
            return
        return User.query.get(id)

    def __repr__(self):
        return f"<User -> username: {self.name}, email: {self.email}, id: {self.id}, visibility: {self.visibility}>"

    def __init__(self, name):
        self._name = name
        self._path = encode(name)


# *************************************************
#  Post
# *************************************************


class Post(KaBase):
    __tablename__ = 'post'

    id = Column(ForeignKey("kabase.id"), primary_key=True)
    text = Column(Text, nullable=False)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    composer = relationship('User', foreign_keys=user_id)
    visibility = Column('visibility', dbEnum(Visibility), default=Visibility.PUBLIC)
    count_favorites = Column(Integer, nullable=False, default=0)
    count_plays = Column(Integer, nullable=False, default=0)

    @hybrid_property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

    @hybrid_property
    def path(self):
        return self._path

    def validate(self):
        assert self.composer, "composer is set in post validation"
        assert self._name, "name is set in post validation"
        self._path = encode(self._name + '__by__' + self.composer.name)

    __searchable__ = ['title', 'content', 'date_posted']

    __mapper_args__ = {
        'polymorphic_identity': 'post',
    }

    def __repr__(self):
        return f"<Post -> id: {self.id}, name: {self.name}, date: {self.created}'>"



# *************************************************
#  Tempo
# *************************************************


@unique
class Tempo(Enum):
    Grave = 'Grave'
    Lento = 'Lento'
    Adagio = 'Adagio'
    Adagietto = 'Adagietto'
    Andante = 'Andante'
    Moderato = 'Moderato'
    Allagretto = 'Allagretto'
    Allegro = 'Allegro'
    Vivace = 'Vivace'
    Presto = 'Presto'

# tempos = [Grave, Lento, Adagio, Adagietto, Andante, Moderato, Allagretto, Allegro, Vivace, Presto]
tempos = [tempo for tempo in Tempo]


# *************************************************
#  Dynamic
# *************************************************


@unique
class Dynamic(Enum):
    Fortissimo = 'Fortissimo'
    Forte = 'Forte'
    Mezzo = 'Mezzo'
    Piano = 'Piano'
    Pianissimo = 'Pianissimo'

# dynamics = [Fortissimo, Forte, Mezzo, Piano, Pianissimo]
dynamics = [dynamic for dynamic in Dynamic]


# *************************************************
#  Measure
# *************************************************


class Measure(KaBase):
    __tablename__ = 'measure'

    id = Column(ForeignKey("kabase.id"), primary_key=True)
    tempo = Column(dbEnum(Tempo), nullable=False, default=Tempo.Moderato)
    dynamic = Column(dbEnum(Dynamic), nullable=False, default=Dynamic.Mezzo)
    text = Column(Text, nullable=False)
    duration = Column(Integer, nullable=False, default=60)
    _ordinal = Column(Integer, nullable=False, default=0)
    score_id = Column(Integer, ForeignKey('score.id'), nullable=False)
    score = relationship('Score', back_populates='measures', foreign_keys=score_id)

    @hybrid_property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

    @hybrid_property
    def path(self):
        return self._path

    @hybrid_property
    def ordinal(self):
        return self._ordinal

    @ordinal.setter
    def ordinal(self, value):
        self._ordinal = value

    def validate(self):
        assert self.score, "score is set in measure validation"
        assert self._name, "name is set in measure validation"
        assert isinstance(self._ordinal, int), "ordinal is set in measure validation"
        self._path = encode(
            f'{self._name}__number__{self._ordinal:04}__from__{self.score.name}__by__{self.score.composer.name}'
        )

    @property
    def formatted_duration(self):
        return pp_duration(self.duration)

    __searchable__ = ['title', 'text']

    __mapper_args__ = {
        'polymorphic_identity': 'measure',
    }

    def __repr__(self):
        return '<Measure -> id: {}, title: {}, ordinal: {}>'.format(self.id, self.name, self.ordinal)



# *************************************************
#  ForPlayers
# *************************************************


class ForPlayers(Enum):
    OneMan = "for a man"
    TwoMen = "for two men"
    OneWoman = "for a woman"
    TwoWomen = "for two women"
    OneAny = "for any one"
    TwoAny = "for any two lovers"
    ManAndWoman = "for man and woman"
    ManAndAny = "for man and lover"
    WomanAndAny = "for woman and lover"

#for_players = [TwoAny, OneAny, ManAndAny, WomanAndAny, ManAndWoman, OneWoman, TwoWomen, OneMan, TwoMen]
for_players = [fp for fp in ForPlayers]


# *************************************************
#  Score
# *************************************************


class Score(KaBase):
    __tablename__ = 'score'

    id = Column(ForeignKey("kabase.id"), primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    composer = relationship('User', foreign_keys=user_id)
    text = Column(Text, nullable=False)
    measures = relationship(
        'Measure',
        back_populates='score',
        foreign_keys='Measure.score_id',
        order_by='Measure.ordinal',
        lazy=True
    )
    duration = Column(Integer, nullable=False, default=0)
    count_plays = Column(Integer, nullable=False, default=0)
    count_favorites = Column(Integer, nullable=False, default=0)
    for_players = Column(dbEnum(ForPlayers), nullable=False, default=ForPlayers.TwoAny)
    visibility = Column('visibility', dbEnum(Visibility), default=Visibility.PUBLIC)
    variation_on_id = Column(Integer, ForeignKey('score.id'), nullable=True)
    variations = relationship(
        "Score",
        backref=backref('variation_on', remote_side=[id]),
        foreign_keys=[variation_on_id],
        lazy=True
    )

    @hybrid_property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

    @hybrid_property
    def path(self):
        return self._path

    def validate(self):
        assert self.composer, "composer is set in score validation"
        assert self._name, "name is set in score validation"
        self._path = encode(
            f'{self._name}__by__{self.composer.name}'
        )
        self._set_duration()

    @property
    def formatted_duration(self):
        return pp_duration(self.duration)

    def _set_duration(self):
        self.duration = sum(m.duration for m in self.measures)

    __searchable__ = ['title', 'description']

    __mapper_args__ = {
        'polymorphic_identity': 'score',
    }

    def __repr__(self):
        return '<Score -> id: {}, name: {}, composer name: {}>'.format(self.id, self.name, self.composer.name)


# *************************************************
#  Favorite
# *************************************************


class Favorite(KaBase):
    __tablename__ = 'favorite'

    id = Column(ForeignKey('kabase.id'), primary_key=True)
    user_id = Column(ForeignKey('user.id'), nullable=False)
    user = relationship('User', foreign_keys=[user_id])
    content_id = Column(ForeignKey('score.id'), nullable=False)
    content = relationship(
        'KaBase',
        foreign_keys=[content_id],
        primaryjoin="and_(Favorite.content_id==KaBase.id)"
    )

    __mapper_args__ = {
        'polymorphic_identity': 'favorite',
    }

    def __init__(self, user_id, content_id):
        self._name = f'favorite__{user_id}__{content_id}'
        self._path = encode(self._name)
        self.user_id = user_id
        self.content_id = content_id



#*************************************************
#  Searchable
# based on https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-xvi-full-text-search
#*************************************************


# from ka.elasticsearch import query_index, remove_from_index, add_to_index, INDEX_PREFIX
#
#
# class SearchableMixin(object):
#     @classmethod
#     def search(cls, expression, page, per_page):
#         ids, total = query_index(cls.index_name(), expression, page, per_page)
#         if total == 0:
#             return Session.query(cls).filter_by(id=0), 0
#         when = []
#         for i in range(len(ids)):
#             when.append((ids[i], i))
#         return Session.query(cls).filter(cls.id.in_(ids)), total  # TODO removed ordering
#
#     @classmethod
#     def before_commit(cls, session):
#         session._changes = {
#             'add': list(session.new),
#             'update': list(session.dirty),
#             'delete': list(session.deleted)
#         }
#
#     @classmethod
#     def after_commit(cls, session):
#         for obj in session._changes['add']:
#             if isinstance(obj, SearchableMixin):
#                 add_to_index(obj.index_name(), obj)
#         for obj in session._changes['update']:
#             if isinstance(obj, SearchableMixin):
#                 add_to_index(obj.index_name(), obj)
#         for obj in session._changes['delete']:
#             if isinstance(obj, SearchableMixin):
#                 remove_from_index(obj.index_name(), obj)
#         session._changes = None
#
#     @classmethod
#     def reindex(cls):
#         for obj in Session.query(cls):
#             add_to_index(cls.index_name(), obj)
#
#     @classmethod
#     def index_name(cls):
#         return INDEX_PREFIX + cls.__tablename__
#
#
# event.listen(Session, 'before_commit', SearchableMixin.before_commit)
# event.listen(Session, 'after_commit', SearchableMixin.after_commit)
