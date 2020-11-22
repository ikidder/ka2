from flask import Blueprint, request, render_template
from flask_login import login_required
from ka.models import Post
import random

main_app = Blueprint('main', __name__)

slogans = ['Empower yourself; Empower your partner.',
    'Be Curious',
    'Go Back for More',
    'Prioritize Intimacy',
    'Love & Intimacy Within the Chaos',
    'Every opportunity is an opportunity to connect more',
    'Our Bodies are Magical Vessels of Pleasure',
    'Luminous Beings Are We',
    'Make Body & Soul Connections',
    'Our bodies are tools with which we can grow our souls',
    'Prioritize pleasure']

@main_app.route("/")
def index():
    slogan = random.choice(slogans)
    return render_template('index.html', title='kamagapē', slogan=slogan)


@main_app.route('/scores', methods=['GET'])
@login_required
def scores():
    return render_template('base.html')


@main_app.route('/not_implemented', methods=['GET'])
@login_required
def not_implemented():
    return render_template('not_implemented.html')


