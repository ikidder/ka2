from flask import Blueprint, request, render_template
from flask_login import login_required
from ka.models import Post

main_app = Blueprint('main', __name__)


@main_app.route("/")
def index():
    return render_template('index.html')


@main_app.route('/scores', methods=['GET'])
@login_required
def scores():
    return render_template('base.html')


@main_app.route('/not_implemented', methods=['GET'])
@login_required
def not_implemented():
    return render_template('not_implemented.html')


