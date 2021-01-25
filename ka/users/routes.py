import datetime
import os
from flask import render_template, url_for, flash, redirect, request, Blueprint, abort
from flask_login import login_user, current_user, logout_user, login_required
from ka import bcrypt, db
from ka.database import get_page
from ka.models import User, Post, Score, Visibility, KaBase, Favorite, Invite, Tag, OpenInvite
from ka.users.forms import (RegistrationForm, LoginForm, UpdateAccountForm,
                                   ResetPasswordRequestForm, ResetPasswordForm, SendInvite, UnsubscribeForm)
import ka.email as email
from sqlalchemy import or_, and_, func
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
        is_existing_user = User.query.filter(User.email == func.lower(form.email.data)).first()
        if is_existing_user:
            render_template('invite.html', title='Invite', success=True)
        invite = Invite.create(current_user, form.email.data)
        db.session.add(invite)
        current_user.invites_left = current_user.invites_left - 1
        db.session.commit()
        email.send_invite_email(invite)
        return render_template('invite.html', title='Invite', success=True)
    return render_template('invite.html', title='Invite', form=form)


@users_app.route("/register/<string:invite_token>", methods=['GET', 'POST'])
def register(invite_token):
    invite = Invite.validate_token(invite_token)
    open_invite = OpenInvite.query.filter(OpenInvite.guid == invite_token).first()
    if invite:
        if invite.user_created:
            print(f'Error: invite already used. Invite.id: {invite.id}')
            return redirect(url_for('main.index'))
        if not invite.responded:
            invite.responded = datetime.datetime.utcnow()
            db.session.commit()
    elif open_invite:
        if not open_invite.is_active():
            abort(404)
    else:
        abort(404)
    form = RegistrationForm()
    if form.validate_on_submit():
        password = str(os.urandom(16))
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

        user = User(name=form.name.data)
        user.email = form.email.data.strip().lower()
        user.password=hashed_password
        db.session.add(user)
        db.session.commit()

        if invite:
            invite.user_created = user.id
            db.session.add(invite)

        db.session.commit()

        token = user.get_reset_password_token()
        email.send_welcome_email(user, token)
        return render_template('registered.html', title='Welcome!')
    return render_template('register.html', title='Register', form=form)


@users_app.route("/create_open_invite/", methods=['GET'])
@login_required
def create_open_invite():
    if not current_user.is_admin:
        abort(403)
    invite = OpenInvite(current_user.id)
    db.session.add(invite)
    db.session.commit()
    url = url_for('users.register', invite_token=invite.guid, _external=True)
    return render_template('create_open_invite.html', title='Invite', url=url)



# *************************************************
#  Log In / Log Out
# *************************************************


@users_app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter(User.email == func.lower(form.email.data)).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('main.index'))
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
        token = current_user.get_reset_password_token()
        email.send_password_reset_email(current_user, token)
        flash('We sent a link to your email address. Please use that link to set your password.', 'success')
        return redirect(url_for('users.login'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter(User.email == func.lower(form.email.data)).first()
        if user:
            token = user.get_reset_password_token()
            email.send_password_reset_email(user, token)
        flash('We sent a link to your email address. Please use that link to set your password.', 'success')
        return redirect(url_for('users.login'))
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
        db.session.add(user)
        db.session.commit()
        logout_user()
        flash('Your password has been set. Please login to continue.', 'success')
        return redirect(url_for('users.login'))
    return render_template('reset_password.html', form=form)


# *************************************************
#  Account / Profile
# *************************************************


@users_app.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        #current_user.email = form.email.data
        current_user.text = form.text.data
        current_user.tags = Tag.extract_tags(current_user.text)
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('users.account'))
    elif request.method == 'GET':
        form.email.data = current_user.email
        form.text.data = current_user.text
    return render_template('account.html', title='Account', form=form)


@users_app.route("/unsubscribe", methods=['GET', 'POST'])
def unsubscribe():
    form = UnsubscribeForm()
    if form.validate_on_submit():
        user = User.query.filter(User.email == func.lower(form.email.data)).first()
        if user:
            user.allow_non_transactional_emails = False
            db.session.add(user)
            db.session.commit()
            flash('You have been unsubscribed.', 'success')
            return redirect(url_for('main.index'))
        else:
            flash('We have received your request to unsubscribe.', 'success')
            return redirect(url_for('main.index'))
    return render_template('unsubscribe.html', title='Unsubscribe', form=form)


# *************************************************
#  Favorites
# *************************************************


@users_app.route('/favorites', methods=['GET'])
@login_required
def favorites():
    favorites = current_user.favorites()
    return render_template(
        'favorites.html',
        title='Favorites',
        favorites=favorites,
        current_user=current_user,
    )


@users_app.route('/favorite/<int:id>/', methods=['GET'])
@login_required
def favorite(id):
    favoritable = with_polymorphic(KaBase, [User, Score, Post])
    obj = db.session.query(favoritable).filter(KaBase.id == id).first()
    if not obj:
        abort(404)
    existing_favorite = current_user.get_favorite(obj.id)
    if existing_favorite:
        existing_favorite.created = datetime.datetime.utcnow()
        db.session.add(existing_favorite)
        db.session.commit()
    else:
        favorite = Favorite(current_user.id, obj.id)
        db.session.add(favorite)
        obj.count_favorites = obj.count_favorites + 1
        db.session.add(obj)
        db.session.commit()
        flash(f'Added "{obj.name}" to Favorites', 'info')
    redirect_path = request.args.get('redirect')
    if redirect_path:
        return redirect(redirect_path)
    else:
        return redirect(url_for('users.favorites'))


@users_app.route('/unfavorite/<int:id>/', methods=['GET'])
@login_required
def unfavorite(id):
    favoritable = with_polymorphic(KaBase, [User, Score, Post])
    obj = db.session.query(favoritable).filter(KaBase.id == id).first()
    if not obj:
        abort(404)
    existing_favorite = current_user.get_favorite(obj.id)
    if not existing_favorite:
        abort(404)
    db.session.delete(existing_favorite)
    obj.count_favorites = obj.count_favorites - 1
    db.session.add(obj)
    db.session.commit()
    flash(f'Removed "{obj.name}" from Favorites', 'info')
    redirect_path = request.args.get('redirect')
    if redirect_path:
        return redirect(redirect_path)
    else:
        redirect(url_for('users.favorites'))


# *************************************************
#  Users and Content
# *************************************************


@users_app.route("/composers")
@login_required
def users():
    page = request.args.get('page', 1, type=int)
    page_result = get_page(
        User.query
            .filter_by(visibility=Visibility.PUBLIC)
            .order_by(User.count_favorites.desc(), (User.count_scores + User.count_posts).desc()),
        page
    )
    return render_template(
        'users.html',
        title='Composers',
        result=page_result
    )


@users_app.route('/composer/<string:user_path>')
@login_required
def user_content(user_path):
    page = request.args.get('page', 1, type=int)
    user = User.query.filter_by(path=user_path).first()
    if not user or user.visibility == Visibility.HIDDEN:
        abort(404)
    content = with_polymorphic(KaBase, [Score, Post])
    page_result = get_page(
        db.session.query(content)
            .filter(or_(content.Score.user_id == user.id, content.Post.user_id == user.id))
            .order_by(content.created.desc()),
        page
    )
    return render_template(
        'user_content.html',
        title='by ' + user.name,
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
