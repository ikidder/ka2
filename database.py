import os
from dataclasses import dataclass

from sqlalchemy import create_engine

from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker

# engine = create_engine(os.environ['DATABASE_URL'])
#
# Session = scoped_session(sessionmaker(bind=engine))


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



# def get_or_404(_type, id):
#     """Based on Flask-SQLAlchemy function
#     https://github.com/pallets/flask-sqlalchemy/blob/95328245ab03ddae97136877e88f18d6bd3cdbee/src/flask_sqlalchemy/__init__.py
#     """
#     rv = Session.query(_type).get(id)
#     if rv is None:
#         abort(404)
#     return rv
#
#
# def first_or_404(_type):
#     """Based on Flask-SQLAlchemy function
#     https://github.com/pallets/flask-sqlalchemy/blob/95328245ab03ddae97136877e88f18d6bd3cdbee/src/flask_sqlalchemy/__init__.py
#     """
#     rv = Session.query(_type).first()
#     if rv is None:
#         abort(404)
#     return rv
#
#
# class Pagination:
#     """Taken entirely from Flask-SQLAlchemy
#     https://github.com/pallets/flask-sqlalchemy/blob/95328245ab03ddae97136877e88f18d6bd3cdbee/src/flask_sqlalchemy/__init__.py
#     """
#
#     def __init__(self, query, page, per_page, total, items):
#         #: the unlimited query object that was used to create this
#         #: pagination object.
#         self.query = query
#         #: the current page number (1 indexed)
#         self.page = page
#         #: the number of items to be displayed on a page.
#         self.per_page = per_page
#         #: the total number of items matching the query
#         self.total = total
#         #: the items for the current page
#         self.items = items
#
#     @property
#     def pages(self):
#         """The total number of pages"""
#         if self.per_page == 0 or self.total is None:
#             pages = 0
#         else:
#             pages = int(ceil(self.total / float(self.per_page)))
#         return pages
#
#     def prev(self, error_out=False):
#         """Returns a :class:`Pagination` object for the previous page."""
#         assert (
#             self.query is not None
#         ), "a query object is required for this method to work"
#         return self.query.paginate(self.page - 1, self.per_page, error_out)
#
#     @property
#     def prev_num(self):
#         """Number of the previous page."""
#         if not self.has_prev:
#             return None
#         return self.page - 1
#
#     @property
#     def has_prev(self):
#         """True if a previous page exists"""
#         return self.page > 1
#
#     def next(self, error_out=False):
#         """Returns a :class:`Pagination` object for the next page."""
#         assert (
#             self.query is not None
#         ), "a query object is required for this method to work"
#         return self.query.paginate(self.page + 1, self.per_page, error_out)
#
#     @property
#     def has_next(self):
#         """True if a next page exists."""
#         return self.page < self.pages
#
#     @property
#     def next_num(self):
#         """Number of the next page"""
#         if not self.has_next:
#             return None
#         return self.page + 1
#
#
#
#
# def paginate(q, page, per_page):
#     """Based on Flask-SQLAlchemy function
#     https://github.com/pallets/flask-sqlalchemy/blob/95328245ab03ddae97136877e88f18d6bd3cdbee/src/flask_sqlalchemy/__init__.py
#     """
#     items = q.limit(per_page).offset((page - 1) * per_page).all()
#
#     if not items and page != 1:
#         abort(404)
#
#     count = len(items)
#
#     return Pagination(self, page, per_page, count, items)