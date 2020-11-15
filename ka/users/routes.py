from flask import render_template, url_for, flash, redirect, request, Blueprint, abort
from flask_login import login_user, current_user, logout_user, login_required
from ka import bcrypt
from ka.database import get_page
from ka import Session
from ka.models import User, Post, Score, Visibility, KaBase
from ka.users.forms import (RegistrationForm, LoginForm, UpdateAccountForm,
                                   RequestResetForm, ResetPasswordForm)
from sqlalchemy import or_
from sqlalchemy.orm import with_polymorphic



users_app = Blueprint('users', __name__)

PER_PAGE = 10


@users_app.route("/register", methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(name=form.name.data, email=form.email.data, password=hashed_password)
        Session.add(user)
        Session.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('users.login'))
    return render_template('register.html', title='Register', form=form)


@users_app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('scores.scores'))
    form = LoginForm()
    if form.validate_on_submit():
        user = Session.query(User).filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('scores.scores'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)


@users_app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('main.index'))


@users_app.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.email = form.email.data
        current_user.text = form.text.data
        Session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('users.account'))
    elif request.method == 'GET':
        form.name.data = current_user.name
        form.email.data = current_user.email
        form.text.data = current_user.text
    return render_template('account.html', title='Account', form=form)


@users_app.route("/users")
@login_required
def users():
    page = request.args.get('page', 1, type=int)
    page_result = get_page(
        Session.query(User)
            .filter_by(visibility=Visibility.PUBLIC)
            .order_by(User.count_favorites.desc(), User.created.desc()),
        page
    )
    return render_template('users.html', result=page_result)


# @users_app.route("/reset_password", methods=['GET', 'POST'])
# def reset_request():
#     if current_user.is_authenticated:
#         return redirect(url_for('main.home'))
#     form = RequestResetForm()
#     if form.validate_on_submit():
#         user = User.query.filter_by(email=form.email.data).first()
#         send_reset_email(user)
#         flash('An email has been sent with instructions to reset your password.', 'info')
#         return redirect(url_for('users.login'))
#     return render_template('reset_request.html', title='Reset Password', form=form)


# @users_app.route("/reset_password/<token>", methods=['GET', 'POST'])
# def reset_token(token):
#     if current_user.is_authenticated:
#         return redirect(url_for('main.index'))
#     user = User.verify_reset_token(token)
#     if user is None:
#         flash('That is an invalid or expired token', 'warning')
#         return redirect(url_for('users.reset_request'))
#     form = ResetPasswordForm()
#     if form.validate_on_submit():
#         hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
#         user.password = hashed_password
#         db.session.commit()
#         flash('Your password has been updated! You are now able to log in', 'success')
#         return redirect(url_for('users.login'))
#     return render_template('reset_token.html', title='Reset Password', form=form)


@users_app.route('/favorites', methods=['GET'])
@login_required
def favorites():
    favorites = current_user.favorites()
    return render_template(
        'favorites.html',
        favorites=favorites,
        current_user=current_user,
    )


@users_app.route('/user/<string:user_path>')
def user_content(user_path):
    page = request.args.get('page', 1, type=int)
    user = Session.query(User).filter_by(path=user_path).first()
    if not user or user.visibility == Visibility.HIDDEN:
        abort(404)
    content = with_polymorphic(KaBase, [Score, Post])
    page_result = get_page(
        Session.query(content)
            .filter(or_(content.Score.user_id == user.id, content.Post.user_id == user.id))
            .order_by(content.created.desc()),
        page
    )
    return render_template(
        'user_content.html',
        filtered_on=user,
        result=page_result,
        current_user=current_user
    )


# *************************************************
#  Template Tests
# *************************************************


@users_app.app_template_test("User")
def is_user(obj):
    return isinstance(obj, User)

@users_app.app_template_test("Score")
def is_score(obj):
    return isinstance(obj, Score)

@users_app.app_template_test("Post")
def is_post(obj):
    return isinstance(obj, Post)
