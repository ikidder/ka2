from flask import Blueprint, request, render_template
from flask_login import login_required
from sqlalchemy.orm import with_polymorphic
from ka.models import KaBase, User, Score, Post, Feature
from ka.database import get_page, PageResult
from ka import db
import random

main_app = Blueprint('main', __name__)


@main_app.route("/")
def index():
    return render_template('index.html', title='')


@main_app.route("/privacy")
def privacy():
    return render_template('legal/privacy.html', title='')


@main_app.route("/terms_of_service")
def terms():
    return render_template('legal/terms.html', title='')


@main_app.route('/featured', methods=['GET'])
@login_required
def featured():
    page = request.args.get('page', 1, type=int)
    content = with_polymorphic(KaBase, [User, Score, Post], flat=True)
    page_result = get_page(
        db.session.query(content)
            .join(Feature, (Feature.content_id == content.id))
            .order_by(Feature.pinned.desc(), Feature.created.desc()),
        page
    )
    return render_template(
        'featured.html',
        result=page_result
    )


@main_app.route('/not_implemented', methods=['GET'])
@login_required
def not_implemented():
    return render_template('not_implemented.html')



# *************************************************
#  Template Tests
# *************************************************


@main_app.app_template_test("User")
def is_user(obj):
    return isinstance(obj, User)

@main_app.app_template_test("Score")
def is_score(obj):
    return isinstance(obj, Score)

@main_app.app_template_test("Post")
def is_post(obj):
    return isinstance(obj, Post)


