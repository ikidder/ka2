from dataclasses import dataclass
from datetime import datetime
from time import time
import re
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app, url_for
import jwt
from urllib.parse import quote
from enum import Enum, unique
from ka import login_manager
from ka import db
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship, backref, validates, joinedload
from sqlalchemy import Enum as dbEnum
from sqlalchemy import and_, or_, Index, func
from sqlalchemy.orm import with_polymorphic
from flask_login import UserMixin


# Reminder: app can be accessed with a flask variable:
#from flask import current_app


# *************************************************
#  Common
# *************************************************


def encode(s):
    """Replaces spaces and url reserved chars.
    Flask automatically escapes arguments to url_for, and automatically unescapes
    route parameters. Therefore, we shouldn't need to call something like:

        quote(s, safe='', encoding='utf-8', errors='strict')

    in this method. However, two characters that are reserved in urls are overlooked
    by url_for: '/' and ':'. """
    s = s.strip()\
        .replace(' ', '-')\
        .replace('/', '%2F')\
        .replace(':', '%3A')
    return s


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
    """Converts an db.Integer into its ordinal representation.
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


@db.event.listens_for(db.session, "before_flush")
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


class KaBase(db.Model):
    __tablename__ = 'kabase'
    id = db.Column(db.Integer, primary_key=True)
    _name = db.Column(db.String(200), nullable=False)
    _path = db.Column(db.String(650), nullable=False)  # see Measure path formatting for the reason this is long
    type = db.Column(db.String(50))
    created = db.Column(db.DateTime, default=datetime.utcnow)

    __mapper_args__ = {
        'polymorphic_identity': 'kabase',
        'polymorphic_on': type
    }

    __table_args__ = (db.Index('_path_type_unique_index', _path, type, unique=True),)


# *************************************************
#  User
# *************************************************


@login_manager.user_loader
def load_player(user_id):
    return User.query.get(int(user_id))


class User(KaBase, UserMixin):
    __tablename__ = 'user'

    id = db.Column(db.ForeignKey("kabase.id"), primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    confirmed = db.Column(db.DateTime, nullable=True)
    password = db.Column(db.String(60), nullable=False)
    visibility = db.Column('visibility', dbEnum(Visibility), default=Visibility.PUBLIC)
    text = db.Column(db.Text, nullable=True, default='')
    count_favorites = db.Column(db.Integer, nullable=False, default=0)
    count_scores = db.Column(db.Integer, nullable=False, default=0)
    count_posts = db.Column(db.Integer, nullable=False, default=0)
    count_tours = db.Column(db.Integer, nullable=False, default=0)
    invites_left = db.Column(db.Integer, nullable=False, default=5)
    is_admin = db.Column(db.Boolean, nullable=False, default=False)
    allow_non_transactional_emails = db.Column(db.Boolean, nullable=False, default=True)

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
        favs = Favorite.query.filter(Favorite.user_id == self.id).all()
        return [fav.content for fav in favs]

    # def favorites(self):
    #     favoritable = with_polymorphic(KaBase, [User, Score, Post], flat=True)
    #     favs = Favorite\
    #         .options(joinedload(Favorite.content.of_type(favoritable)))\
    #         .filter(Favorite.user_id == self.id)\
    #         .order_by(Favorite.created.desc())\
    #         .all()
    #     return [fav.content for fav in favs]
    #

    def get_favorite(self, kabase_id):
        return Favorite.query \
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
        except Exception as ex:
            print(ex)
            return
        return User.query.get(id)

    def __repr__(self):
        return f"<User -> username: {self.name}, email: {self.email}, id: {self.id}, visibility: {self.visibility}>"

    def __init__(self, name):
        self._name = name.strip()
        assert not self._name.startswith('&'), 'titles cannot start with the theme character'
        assert '_' not in self._name, 'no underscores in user names'
        self._path = encode(name)


# *************************************************
#  Post
# *************************************************


class Post(KaBase):
    __tablename__ = 'post'

    id = db.Column(db.ForeignKey("kabase.id"), primary_key=True)
    text = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    composer = relationship('User', foreign_keys=user_id)
    visibility = db.Column('visibility', dbEnum(Visibility), default=Visibility.PUBLIC)
    count_favorites = db.Column(db.Integer, nullable=False, default=0)
    count_plays = db.Column(db.Integer, nullable=False, default=0)

    @hybrid_property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value.strip()

    @hybrid_property
    def path(self):
        return self._path

    def validate(self):
        assert self.composer, "composer is set in post validation"
        assert self._name, "name is set in post validation"
        assert not self._name.startswith('&'), 'titles cannot start with the theme character'
        assert '_' not in self._name, 'no underscores in score names'
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
    Allegretto = 'Allegretto'
    Allegro = 'Allegro'
    Vivace = 'Vivace'
    Presto = 'Presto'


tempos = [tempo for tempo in Tempo]

tempo_alt_text = {
    Tempo.Grave: '20 - 40 bpm. Very slow and solemn.',
    Tempo.Lento: '40 - 60 bpm. Slowly.',
    Tempo.Adagio: '66 - 76 bpm. At ease.',
    Tempo.Adagietto: '70 - 80 bpm. Rather slow.',
    Tempo.Andante: '76 - 108 bpm. A walking pace.',
    Tempo.Moderato: '108 - 120 bpm. A moderate speed.',
    Tempo.Allegretto: '112 - 120 bpm. Moderately fast.',
    Tempo.Allegro: '120 - 156 bpm. Fast, quick, and bright. A heartbeat.',
    Tempo.Vivace: '156 - 176 bpm. Lively and fast.',
    Tempo.Presto: '176 - 200 bpm. Very, very fast.'
}


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


dynamics = list(reversed([dynamic for dynamic in Dynamic]))

dynamic_alt_text = {
    Dynamic.Pianissimo: 'As soft as possible. Touching an ear lobe without moving it, or feeling the seeds of a strawberry.',
    Dynamic.Piano: 'Soft, gentle. Skin barely moves under the touch. Like drawing in the icing of a cake.',
    Dynamic.Mezzo: 'Moderate, intentional pressure. Like peeling an orange.',
    Dynamic.Forte: 'Firm. Like testing a grapefruit for ripeness.',
    Dynamic.Fortissimo: 'Very firm. Like kneading muscles, or dough, or squeezing juice.',
}


# *************************************************
#  Measure
# *************************************************


class Measure(KaBase):
    __tablename__ = 'measure'

    id = db.Column(db.ForeignKey("kabase.id"), primary_key=True)
    tempo = db.Column(dbEnum(Tempo), nullable=False, default=Tempo.Moderato)
    dynamic = db.Column(dbEnum(Dynamic), nullable=False, default=Dynamic.Mezzo)
    text = db.Column(db.Text, nullable=False)
    duration = db.Column(db.Integer, nullable=False, default=60)
    _ordinal = db.Column(db.Integer, nullable=False, default=0)
    score_id = db.Column(db.Integer, db.ForeignKey('score.id'), nullable=False)
    score = relationship('Score', back_populates='measures', foreign_keys=score_id)

    @hybrid_property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value.strip()

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
        assert not self._name.startswith('&'), 'titles cannot start with the theme character'
        assert '_' not in self._name, 'no underscores in measure names'
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

    id = db.Column(db.ForeignKey("kabase.id"), primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    composer = relationship('User', foreign_keys=user_id)
    text = db.Column(db.Text, nullable=False)
    measures = relationship(
        'Measure',
        back_populates='score',
        foreign_keys='Measure.score_id',
        order_by='Measure.ordinal',
        lazy=True
    )
    duration = db.Column(db.Integer, nullable=False, default=0)
    count_plays = db.Column(db.Integer, nullable=False, default=0)
    count_favorites = db.Column(db.Integer, nullable=False, default=0)
    for_players = db.Column(dbEnum(ForPlayers), nullable=False, default=ForPlayers.TwoAny)
    visibility = db.Column('visibility', dbEnum(Visibility), default=Visibility.PUBLIC)
    variation_on_id = db.Column(db.Integer, db.ForeignKey('score.id'), nullable=True)
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
        self._name = value.strip()

    @hybrid_property
    def path(self):
        return self._path

    def validate(self):
        assert self.composer, "composer is set in score validation"
        assert self._name, "name is set in score validation"
        assert not self._name.startswith('&'), 'titles cannot start with the theme character'
        assert '_' not in self._name, 'no underscores in score names'
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

    id = db.Column(db.ForeignKey('kabase.id'), primary_key=True)
    user_id = db.Column(db.ForeignKey('user.id'), nullable=False)
    user = relationship('User', foreign_keys=[user_id], )
    content_id = db.Column(db.ForeignKey('kabase.id'), nullable=False)
    content = relationship(
        'KaBase',
        foreign_keys=[content_id],
        primaryjoin="Favorite.content_id==KaBase.id"
    )

    __mapper_args__ = {
        'polymorphic_identity': 'favorite',
        'inherit_condition': id == KaBase.id
    }

    def __init__(self, user_id, content_id):
        self._name = f'favorite__{user_id}__{content_id}'
        self._path = encode(self._name)
        self.user_id = user_id
        self.content_id = content_id

    def __repr__(self):
        return f'<Favorite -> id: {self.id}, user_id: {self.user_id}, content_id: {self.content_id}>'



# *************************************************
#  Featured
# *************************************************


class Feature(KaBase):
    __tablename__ = 'feature'

    id = db.Column(db.ForeignKey('kabase.id'), primary_key=True)
    pinned = db.Column(db.Boolean, nullable=False, default=False)
    content_id = db.Column(db.ForeignKey('kabase.id'), nullable=False)
    content = relationship(
        'KaBase',
        foreign_keys=[content_id],
        primaryjoin="Feature.content_id==KaBase.id"
    )

    __mapper_args__ = {
        'polymorphic_identity': 'feature',
        'inherit_condition': id == KaBase.id
    }

    def __init__(self, content_id, pinned=False):
        self._name = f'feature__{content_id}'
        self._path = encode(self._name)
        self.pinned = pinned
        self.content_id = content_id

    def __repr__(self):
        return f'<Feature -> id: {self.id}, content_id: {self.content_id}, pinned: {self.pinned}>'



# *************************************************
#  Invite
# *************************************************

INVITE_GOOD_FOR = 604800  # in seconds. == 7 days


class Invite(db.Model):
    __tablename__ = 'invite'

    id = db.Column(db.Integer, primary_key=True)
    from_user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    to_email = db.Column(db.String(120), nullable=False)
    created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    responded = db.Column(db.DateTime, nullable=True)
    user_created = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)

    def token(self):
        assert self.id, "Invite.id is set."
        assert self.from_user_id, "from_user_id is set"
        assert len(self.to_email) > 6 and '@' in self.to_email, "to_email looks like an email"
        return jwt.encode(
            {'inv_id': self.id, 'exp': time() + INVITE_GOOD_FOR, 'to_email': self.to_email},
            current_app.config['SECRET_KEY'],
            algorithm='HS256'
        ).decode('utf-8')

    @classmethod
    def create(cls, from_user, to_email):
        inv = Invite(from_user_id=from_user.id, to_email=to_email, created=datetime.utcnow())
        return inv

    @staticmethod
    def validate_token(token):
        try:
            id = jwt.decode(token, current_app.config['SECRET_KEY'],
                            algorithms=['HS256'])['inv_id']
        except Exception as ex:
            print(ex)
            return
        return Invite.query.get(id)

    def __repr__(self):
        return f'<Invite -> id: {self.id}, from_user_id: {self.from_user_id}, created: {self.created}, user_created: {self.user_created}>'


# *************************************************
#  Tag
# *************************************************


TAG_REGEX = r'(?:^|[;,.?!\s])(&[^\W_]{2,30})(?=[;,.?!\s]|$)'
pattern = re.compile(TAG_REGEX)

tag_association = db.Table(
    'tag_association',
    db.metadata,
    db.Column('tag_id', db.Integer, db.ForeignKey('tag.id')),
    db.Column('tagged_id', db.Integer, db.ForeignKey('kabase.id'))
)


class Tag(KaBase):
    __tablename__ = 'tag'

    id = db.Column(db.ForeignKey('kabase.id'), primary_key=True)
    tagged = relationship("KaBase",
                    secondary=tag_association,
                    backref="tags")

    __mapper_args__ = {
        'polymorphic_identity': 'tag',
        'inherit_condition': id == KaBase.id
    }

    @hybrid_property
    def name(self):
        return self._name

    @hybrid_property
    def path(self):
        return self._path

    def __init__(self, name):
        self._name = name.strip()
        assert self._name[0] == '&', 'tags must start with a &'
        assert len(self._name) > 2, 'tags must be at least three chars long, after the &'
        assert '&' not in self._name[1:], "no &'s after the first char in a tag"
        assert '_' not in self._name, 'no underscores in tag names'
        self._path = encode(self._name)

    def __repr__(self):
        return f'<Tag -> id: {self.id}, name: {self.name}>'

    @staticmethod
    def tag_counts():
        sql = """select _name, count(*)
from kabase 
inner join tag 
on kabase.id = tag.id
inner join tag_association
on tag.id = tag_association.tag_id
group by _name
order by _name"""
        result_proxy = db.engine.execute(sql)
        return [item for item in result_proxy]

    @staticmethod
    def extract_tags(text):
        """Extracts tags that should be with the object holding the given text."""
        matches = pattern.findall(text)
        limited_unique_matches = list(dict.fromkeys(matches))[:4]
        tags = []
        for match in limited_unique_matches:
            tag = Tag.query.filter(Tag.name == match).first()
            if not tag:
                tag = Tag(match)
            tags.append(tag)
        return tags



# *************************************************
#  Event
# *************************************************


class HttpEvent(db.Model):
    __tablename__ = 'event'

    id = db.Column(db.Integer, primary_key=True)
    datestamp = db.Column(db.DateTime, default=datetime.utcnow())
    user = db.Column(db.Integer, nullable=True)
    method = db.Column(db.String(20), nullable=True)
    path = db.Column(db.Text, nullable=True)
    query = db.Column(db.Text, nullable=True)
    status_code = db.Column(db.Integer, nullable=True)
    ellapsed_time = db.Column(db.Integer, nullable=True)
    referrer = db.Column(db.Text, nullable=True)
    requesting_addr = db.Column(db.Text, nullable=True)
    responding_addr = db.Column(db.Text, nullable=True)
    user_agent = db.Column(db.Text, nullable=True)

    __table_args__ = (db.Index('_datestamp_index', datestamp),)


mymodel_url_index = Index('http_event_datestamp_index', HttpEvent.datestamp)


class EventAggregate(db.Model):
    __tablename__ = 'event_aggregate'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text)  # what kind of an aggregate is this, e.g. counting page hits, 404's, etc.
    value = db.Column(db.Text, nullable=True)  # the specific value for this kind of aggregate, e.g. page hits for '/'
    start_range = db.Column(db.DateTime)
    end_range = db.Column(db.DateTime)
    count = db.Column(db.Integer)

    __table_args__ = (db.Index('_name_index', name),)


def top_pages(start, end, limit=20):
    return HttpEvent.query\
        .with_entities(HttpEvent.path, func.count(HttpEvent.path))\
        .filter(and_(HttpEvent.datestamp >= start, HttpEvent.datestamp <= end))\
        .group_by(HttpEvent.path)\
        .order_by(func.count(HttpEvent.path).desc())\
        .limit(limit)\
        .all()


def objects_created(start, end, limit=20):
    return HttpEvent.query\
        .with_entities(HttpEvent.path, func.count(HttpEvent.path))\
        .filter(and_(HttpEvent.datestamp >= start, HttpEvent.datestamp <= end))\
        .filter(or_(HttpEvent.path == '/score/new', HttpEvent.path.like('/score/%/copy')))\
        .group_by(HttpEvent.path)\
        .order_by(func.count(HttpEvent.path).desc())\
        .limit(limit)\
        .all()



