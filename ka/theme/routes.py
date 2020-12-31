from flask import Blueprint, request, render_template, abort
from flask_login import login_required
from sqlalchemy.orm import with_polymorphic
from sqlalchemy import func
from ka.models import KaBase, Tag, tag_association, User, Score, Post
from ka.database import get_page, PageResult
from ka import db

theme_app = Blueprint('theme', __name__)


@theme_app.route('/themes', methods=['GET'])
@login_required
def themes():
    results = Tag.tag_counts()
    return render_template(
        'themes.html',
        title='Themes',
        results=results
    )


@theme_app.route('/theme/<string:name>', methods=['GET'])
@login_required
def theme(name):
    page = request.args.get('page', 1, type=int)
    t = Tag.query.filter(Tag.name == name).first()
    if not t:
        abort(404)
    content = with_polymorphic(KaBase, [User, Score, Post], flat=True)
    page_result = get_page(
        db.session.query(content)\
        .select_from(Tag)\
        .join(tag_association)\
        .join(content)\
        .filter(tag_association.c.tag_id == t.id)
        .order_by(content.created.desc()),
        page
    )
    return render_template(
        'theme.html',
        title=t.name + ' themed',
        name=name,
        result=page_result
    )