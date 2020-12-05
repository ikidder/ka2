from flask import (render_template, url_for, flash,
                   redirect, request, abort, Blueprint)
from flask_login import current_user, login_required
from ka.database import get_page
from ka import db
from ka.models import Post, Visibility, User
from ka.posts.forms import PostForm, DeletePostForm
from sqlalchemy import or_


posts_app = Blueprint('posts', __name__)


@posts_app.route("/post/new", methods=['GET', 'POST'])
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(name=form.name.data, text=form.text.data, composer=current_user)
        post.composer.count_posts = post.composer.count_posts + 1
        db.session.add(post)
        db.session.commit()
        flash('Your post has been created!', 'success')
        return redirect(url_for('posts.posts'))
    return render_template('create_post.html', title='New Post',
                           form=form, legend='New Post')


@posts_app.route("/post/<string:post_path>")
@login_required
def post(post_path):
    p = Post.query.filter_by(path=post_path).first()
    if not p:
        abort(404)
    if p.visibility == Visibility.HIDDEN:
        abort(404)
    return render_template('post.html', title=p.name, post=p)


@posts_app.route("/post/<string:post_path>/update", methods=['GET', 'POST'])
@login_required
def update_post(post_path):
    p = Post.query.filter_by(path=post_path).first()
    if not p:
        abort(404)
    if p.composer != current_user:
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        p.name = form.name.data
        p.text = form.text.data
        db.session.commit()
        flash('Your post has been updated!', 'success')
        return redirect(url_for('posts.post', post_path=p.path))
    elif request.method == 'GET':
        form.name.data = p.name
        form.text.data = p.text
    return render_template('create_post.html', title='Edit Post',
                           form=form, legend='Edit Post')


@posts_app.route("/post/<string:post_path>/delete", methods=['GET','POST'])
@login_required
def delete_post(post_path):
    p = Post.query.filter_by(path=post_path).first()
    if not p:
        abort(404)
    if p.user_id != current_user.id:
        abort(403)

    form = DeletePostForm()
    if form.validate_on_submit():
        p.composer.count_posts = p.composer.count_posts - 1
        db.session.delete(p)
        db.session.commit()
        flash('Your post has been deleted!', 'success')
        return redirect(url_for('posts.posts'))

    return render_template('delete_post.html', title='Delete Post', form=form, post=p)


@posts_app.route('/posts', methods=['GET'])
@login_required
def posts():
    page = request.args.get('page', 1, type=int)
    page_result = get_page(
        Post.query
            .filter_by(visibility=Visibility.PUBLIC)
            .order_by(Post.created.desc()),
        page
    )
    return render_template('posts.html', result=page_result)


@posts_app.route("/user/<string:user_path>/posts")
@login_required
def user_posts(user_path):
    page = request.args.get('page', 1, type=int)
    user = User.query.filter_by(path=user_path).first()
    if not user:
        abort(404)
    page_result = get_page(
        Post.query
            .filter(Post.user_id == user.id)
            .filter(or_(Post.visibility == Visibility.PUBLIC, Post.visibility == Visibility.PRIVATE))
            .order_by(Post.count_favorites.desc(), Post.created.desc()),
        page
    )
    return render_template(
        'user_posts.html',
        filtered_on=user,
        result=page_result
    )



# *************************************************
#  Template Tests
# *************************************************


@posts_app.app_template_test("User")
def is_user(o):
    return isinstance(o, User)

