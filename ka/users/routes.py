import datetime
import os
from flask import render_template, url_for, flash, redirect, request, Blueprint, abort
from flask_login import login_user, current_user, logout_user, login_required
from ka import bcrypt
from ka.database import get_page
from ka import Session
from ka.models import User, Post, Score, Visibility, KaBase, Favorite, Invite
from ka.users.forms import (RegistrationForm, LoginForm, UpdateAccountForm,
                                   ResetPasswordRequestForm, ResetPasswordForm, SendInvite)
import ka.email as email
from sqlalchemy import or_, and_
from sqlalchemy.orm import with_polymorphic


users_app = Blueprint('users', __name__)

PER_PAGE = 10


# *************************************************
#  Invite
# *************************************************


@users_app.route("/send_invite/", methods=['GET', 'POST'])
@login_required
def send_invite():
    form = SendInvite()
    if form.validate_on_submit():
        if current_user.invites_left < 1:
            flash('No invites left.', 'danger')
            render_template('invite.html', title='Invite', form=form)
        is_existing_user = Session.query(User).filter_by(email=form.email.data).first()
        if is_existing_user:
            render_template('invite.html', title='Invite', success=True)
        invite = Invite.create(current_user, form.email.data)
        Session.add(invite)
        current_user.invites_left = current_user.invites_left - 1
        Session.commit()
        email.send_invite_email(invite)
        return render_template('invite.html', title='Invite', success=True)
    return render_template('invite.html', title='Invite', form=form)


@users_app.route("/register/<string:invite_token>", methods=['GET', 'POST'])
def register(invite_token):
    invite = Invite.validate_token(invite_token)
    if not invite:
        print(f'Error: failed invite token validation: {invite_token}')
        return redirect(url_for('main.index'))
    if invite.user_created:
        print(f'Error: invite already used. Invite.id: {invite.id}')
        return redirect(url_for('main.index'))
    if not invite.responded:
        invite.responded = datetime.datetime.utcnow()
        Session.commit()
    form = RegistrationForm()
    if form.validate_on_submit():
        password = str(os.urandom(16))
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

        user = User(name=form.name.data)
        user.email = form.email.data.strip()
        user.password=hashed_password
        Session.add(user)
        Session.commit()

        invite.user_created = user.id
        Session.add(invite)
        Session.commit()

        token = user.get_reset_password_token()
        email.send_welcome_email(user, token)
        return render_template('registered.html', title='Welcome!')
    return render_template('register.html', title='Register', form=form)


# *************************************************
#  Log In / Log Out
# *************************************************


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


@users_app.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            token = user.get_reset_password_token()
            email.send_password_reset_email(user, token)
        flash('Check your email for the instructions to reset your password')
        return redirect(url_for('login'))
    return render_template('reset_password_request.html',
                           title='Reset Password', form=form)


@users_app.route('/reset_password/<string:token>', methods=['GET', 'POST'])
def reset_password(token):
    user = User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for('scores.scores'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        if not user.confirmed:
            user.confirmed = datetime.datetime.utcnow()
        Session.add(user)
        Session.commit()
        logout_user()
        flash('Your password has been set. Please login to continue.')
        return redirect(url_for('login'))
    return render_template('reset_password.html', form=form)


# *************************************************
#  Account / Profile
# *************************************************


@users_app.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        current_user.email = form.email.data
        current_user.text = form.text.data
        Session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('users.account'))
    elif request.method == 'GET':
        form.email.data = current_user.email
        form.text.data = current_user.text
    return render_template('account.html', title='Account', form=form)





# *************************************************
#  Favorites
# *************************************************


@users_app.route('/favorites', methods=['GET'])
@login_required
def favorites():
    favorites = current_user.favorites()
    return render_template(
        'favorites.html',
        favorites=favorites,
        current_user=current_user,
    )


@users_app.route('/favorite/<int:id>/', methods=['GET'])
@login_required
def favorite(id):
    favoritable = with_polymorphic(KaBase, [User, Score, Post])
    obj = Session.query(favoritable).filter(KaBase.id == id).first()
    if not obj:
        abort(404)
    existing_favorite = current_user.get_favorite(obj.id)
    if existing_favorite:
        existing_favorite.created = datetime.datetime.utcnow()
        Session.add(existing_favorite)
        Session.commit()
    else:
        favorite = Favorite(current_user.id, obj.id)
        Session.add(favorite)
        obj.count_favorites = obj.count_favorites + 1
        Session.add(obj)
        Session.commit()
        flash(f'Added "{obj.name}" to Favorites')
    redirect_path = request.args.get('redirect')
    if redirect_path:
        return redirect(redirect_path)
    else:
        redirect(url_for('users.favorites'))


@users_app.route('/unfavorite/<int:id>/', methods=['GET'])
@login_required
def unfavorite(id):
    favoritable = with_polymorphic(KaBase, [User, Score, Post])
    obj = Session.query(favoritable).filter(KaBase.id == id).first()
    if not obj:
        abort(404)
    existing_favorite = current_user.get_favorite(obj.id)
    if not existing_favorite:
        abort(404)
    Session.delete(existing_favorite)
    obj.count_favorites = obj.count_favorites - 1
    Session.add(obj)
    Session.commit()
    flash(f'Removed "{obj.name}" from Favorites')
    redirect_path = request.args.get('redirect')
    if redirect_path:
        return redirect(redirect_path)
    else:
        redirect(url_for('users.favorites'))


# *************************************************
#  Users and Content
# *************************************************


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
        result=page_result
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
